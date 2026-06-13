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
    QDialogButtonBox, QHBoxLayout, QPlainTextEdit, QPushButton,
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
        """Update context from current project/document."""
        if not self._session:
            return
        project = SHARED.project
        if project and project.storage:
            context = []
            context.append(f"Project: {project.data.name}")
            context.append(f"Author: {project.data.author}")
            if current := SHARED.currentDocument:
                if doc := current.doc:
                    context.append(f"Current Document: {doc.itemName}")
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
        """Run the AI operation."""
        self.btnGenerate.setEnabled(False)
        self.resultArea.setPlainText(self.tr("Generating..."))
        QThread.safeProcessEvents()  # type: ignore

        settings = CONFIG.aiSettings
        try:
            provider = create_provider(
                settings.provider_type,
                settings.get_provider_config(),
            )
            completion = AICompletion(provider)

            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                if operation == "continue":
                    result = loop.run_until_complete(completion.complete(text))
                elif operation == "rewrite":
                    result = loop.run_until_complete(completion.rewrite(text))
                elif operation == "expand":
                    result = loop.run_until_complete(completion.expand(text))
                elif operation == "summarize":
                    result = loop.run_until_complete(completion.summarize(text))
                else:
                    result = "Unknown operation"
            finally:
                loop.close()

            self._resultText = result
            self.resultArea.setPlainText(result)
            self.btnApply.setEnabled(True)

        except Exception as exc:
            self.resultArea.setPlainText(f"Error: {exc}")

        self.btnGenerate.setEnabled(True)

    def _applyResult(self) -> None:
        """Emit the result and close."""
        self.resultReady.emit(self._resultText)
        self.close()
