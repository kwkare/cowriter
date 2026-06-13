"""
CoWriter – AI Chat Panel
========================
AI assistant chat panel for the main GUI.
"""

from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QApplication, QDialogButtonBox, QHBoxLayout, QPlainTextEdit, QPushButton,
    QScrollArea, QTextBrowser, QVBoxLayout, QWidget
)
from cowriter import CONFIG, SHARED
from cowriter.ai.chat import AIChatSession
from cowriter.ai.completion import AICompletion
from cowriter.ai.provider import create_provider
from cowriter.ai.settings import AISettings
from cowriter.enum import nwStandardButton
from cowriter.extensions.modified import NNonBlockingDialog
from cowriter.extensions.switch import NSwitch

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QWidget as _QWidget

logger = logging.getLogger(__name__)


class AIWorker(QThread):
    """Worker thread for AI requests to avoid blocking the UI."""

    responseReady = pyqtSignal(str)
    streamChunk = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, session: AIChatSession, message: str) -> None:
        super().__init__()
        self._session = session
        self._message = message
        self._running = True

    def run(self) -> None:
        """Run the AI request in a thread."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(
                self._session.send(self._message)
            )
            self.responseReady.emit(response)
        except Exception as exc:
            self.responseReady.emit(f"Error: {exc}")
        finally:
            loop.close()
            self.finished.emit()

    def stop(self) -> None:
        """Stop the worker."""
        self._running = False


class GuiAIChatPanel(NNonBlockingDialog):
    """AI Chat Assistant Panel."""

    def __init__(self, parent: _QWidget) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiAIChatPanel")
        self.setObjectName("GuiAIChatPanel")
        self.setWindowTitle("AI Chat")

        self._settings: AISettings = CONFIG.aiSettings
        self._session: AIChatSession | None = None
        self._worker: AIWorker | None = None

        self.setMinimumSize(400, 500)
        self.resize(480, 600)

        # Chat display
        self.chatDisplay = QTextBrowser(self)
        self.chatDisplay.setOpenExternalLinks(True)
        self.chatDisplay.setReadOnly(True)

        # Input area
        self.inputEdit = QPlainTextEdit(self)
        self.inputEdit.setPlaceholderText(self.tr("Ask AI for writing help..."))
        self.inputEdit.setMaximumBlockCount(20)
        self.inputEdit.setFixedHeight(80)

        # Send button
        self.sendButton = QPushButton(self.tr("Send"), self)
        self.sendButton.clicked.connect(self._sendMessage)

        # Clear button
        self.clearButton = QPushButton(self.tr("Clear"), self)
        self.clearButton.clicked.connect(self._clearChat)

        # Input layout
        inputRow = QHBoxLayout()
        inputRow.addWidget(self.inputEdit, 1)
        inputRow.addWidget(self.sendButton)
        inputRow.addWidget(self.clearButton)

        # Assemble
        self.outerBox = QVBoxLayout(self)
        self.outerBox.addWidget(self.chatDisplay, 1)
        self.outerBox.addLayout(inputRow)

        # Keyboard shortcut: Enter to send
        self.inputEdit.installEventFilter(self)

        # Connect to project changes
        if SHARED.project:
            self._updateContext()

        logger.debug("Ready: GuiAIChatPanel")

    def _ensureSession(self) -> AIChatSession:
        """Ensure a chat session exists."""
        if self._session is None:
            settings = CONFIG.aiSettings
            provider = create_provider(
                settings.provider_type,
                settings.get_provider_config(),
            )
            self._session = AIChatSession(provider)
            self._updateContext()
        return self._session

    def _updateContext(self) -> None:
        """Update context from current project."""
        if not self._session:
            return
        project = SHARED.project
        if project and project.storage:
            context = []
            context.append(f"Project: {project.data.name}")
            context.append(f"Author: {project.data.author}")
            self._session.set_context("\n".join(context))

    def _sendMessage(self) -> None:
        """Send the current message to AI."""
        message = self.inputEdit.toPlainText().strip()
        if not message:
            return

        self.inputEdit.setPlainText("")
        self.sendButton.setEnabled(False)

        # Display user message
        self.chatDisplay.append(
            f'<p style="color: #4488ff;"><b>You:</b></p>'
            f'<p>{message}</p>'
        )

        # Send to AI
        try:
            session = self._ensureSession()
            self._worker = AIWorker(session, message)
            self._worker.responseReady.connect(self._onResponse)
            self._worker.finished.connect(self._onWorkerFinished)
            self._worker.start()
        except Exception as exc:
            self.chatDisplay.append(
                f'<p style="color: #ff4444;"><b>Error:</b> {exc}</p>'
            )
            self.sendButton.setEnabled(True)

    @pyqtSlot(str)
    def _onResponse(self, response: str) -> None:
        """Handle AI response."""
        self.chatDisplay.append(
            f'<p style="color: #44aa44;"><b>AI:</b></p>'
            f'<p>{response}</p>'
        )
        # Scroll to bottom
        scrollbar = self.chatDisplay.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())

    @pyqtSlot()
    def _onWorkerFinished(self) -> None:
        """Handle worker completion."""
        self.sendButton.setEnabled(True)
        self._worker = None

    def _clearChat(self) -> None:
        """Clear the chat display and session."""
        self.chatDisplay.clear()
        if self._session:
            self._session.clear()
        self._session = None

    def closeEvent(self, event: object) -> None:
        """Clean up on close."""
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(2000)
        super().closeEvent(event)  # type: ignore


class GuiAICompleteDialog(NNonBlockingDialog):
    """Dialog for AI completion/rewrite operations."""

    resultReady = pyqtSignal(str)

    def __init__(self, parent: _QWidget, operation: str, text: str) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiAICompleteDialog")
        self.setObjectName("GuiAICompleteDialog")

        op_titles = {
            "continue": self.tr("AI Continue Writing"),
            "rewrite": self.tr("AI Rewrite"),
            "expand": self.tr("AI Expand"),
            "summarize": self.tr("AI Summarize"),
        }
        self.setWindowTitle(op_titles.get(operation, self.tr("AI Assistant")))
        self.setMinimumSize(500, 400)

        # Original text
        self.originalLabel = QPlainTextEdit(self)
        self.originalLabel.setPlainText(text)
        self.originalLabel.setReadOnly(True)
        self.originalLabel.setMaximumHeight(150)

        # Result area
        self.resultArea = QTextBrowser(self)
        self.resultArea.setOpenExternalLinks(False)

        # Buttons
        self.btnGenerate = QPushButton(self.tr("Generate"), self)
        self.btnGenerate.clicked.connect(lambda: self._runOperation(operation, text))

        self.btnApply = QPushButton(self.tr("Apply"), self)
        self.btnApply.clicked.connect(self._applyResult)
        self.btnApply.setEnabled(False)

        self.btnCancel = QPushButton(self.tr("Cancel"), self)
        self.btnCancel.clicked.connect(self.close)

        btnRow = QHBoxLayout()
        btnRow.addWidget(self.btnGenerate)
        btnRow.addStretch(1)
        btnRow.addWidget(self.btnApply)
        btnRow.addWidget(self.btnCancel)

        # Assemble
        self.outerBox = QVBoxLayout(self)
        self.outerBox.addWidget(self.originalLabel)
        self.outerBox.addWidget(self.resultArea, 1)
        self.outerBox.addLayout(btnRow)

        self._resultText = ""
        self._operation = operation

        logger.debug("Ready: GuiAICompleteDialog")

    def _runOperation(self, operation: str, text: str) -> None:
        """Run the AI operation in a background thread."""
        self.btnGenerate.setEnabled(False)
        self.resultArea.setPlainText(self.tr("Generating..."))
        QApplication.processEvents()

        from cowriter.ai.provider import create_provider
        from cowriter.ai.completion import AICompletion

        settings = CONFIG.aiSettings
        try:
            provider = create_provider(
                settings.provider_type,
                settings.get_provider_config(),
            )
            completion = AICompletion(provider)
        except Exception as exc:
            self.resultArea.setPlainText(f"Provider error: {exc}")
            self.btnGenerate.setEnabled(True)
            return

        # Run in a QThread to avoid blocking the UI
        self._worker = _CompletionWorker(completion, operation, text)
        self._worker.resultReady.connect(self._onCompletionResult)
        self._worker.errorOccurred.connect(self._onCompletionError)
        self._worker.finished.connect(lambda: self.btnGenerate.setEnabled(True))
        self._worker.start()

    @pyqtSlot(str)
    def _onCompletionResult(self, result: str) -> None:
        self._resultText = result
        self.resultArea.setPlainText(result)
        self.btnApply.setEnabled(True)

    @pyqtSlot(str)
    def _onCompletionError(self, error: str) -> None:
        self.resultArea.setPlainText(f"Error: {error}")

    @pyqtSlot()
    def _applyResult(self) -> None:
        """Emit the result and close."""
        self.resultReady.emit(self._resultText)
        self.close()


class _CompletionWorker(QThread):
    """Worker thread for AI completion operations."""

    resultReady = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)

    def __init__(
        self, completion: AICompletion, operation: str, text: str
    ) -> None:
        super().__init__()
        self._completion = completion
        self._operation = operation
        self._text = text

    def run(self) -> None:
        """Run the AI operation in a thread-safe way."""
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                ops = {
                    "continue": self._completion.complete,
                    "rewrite": self._completion.rewrite,
                    "expand": self._completion.expand,
                    "summarize": self._completion.summarize,
                }
                if fn := ops.get(self._operation):
                    result = loop.run_until_complete(fn(self._text))
                else:
                    result = "Unknown operation"
            finally:
                loop.close()
            self.resultReady.emit(result)
        except Exception as exc:
            error_msg = str(exc)
            # Handle encoding issues in error messages
            try:
                error_msg.encode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                error_msg = error_msg.encode("utf-8", errors="replace").decode("utf-8")
            self.errorOccurred.emit(error_msg)

