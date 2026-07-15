"""Drag & drop visual overlay for the Excel Automation Toolkit.

Displays a semi-transparent fullscreen overlay with a dashed green border,
an Excel icon, and instructional text whenever the user drags an Excel file
over the main window.  The widget drives its own fade-in / fade-out
animations via a single, permanently-connected QPropertyAnimation finished
signal so that repeated drag operations never accumulate stale connections.
"""

from __future__ import annotations

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    Qt,
    QTimer,
)
from PySide6.QtGui import (
    QColor,
    QCursor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QWidget

# ---------------------------------------------------------------------------
# Design tokens — tweak here to restyle without touching logic
# ---------------------------------------------------------------------------

_BG_COLOR = QColor(15, 20, 15, 210)
_BORDER_COLOR_ALPHA = QColor(52, 199, 89, 180)

_TITLE_COLOR = QColor(230, 255, 230)
_SUBTITLE_COLOR = QColor(150, 210, 150)

_CARD_PADDING = 60
_BORDER_RADIUS = 18
_BORDER_WIDTH = 2.5
_DASH_PATTERN = [10.0, 6.0]

_FADE_IN_MS = 180
_FADE_OUT_MS = 140

# How long we wait after a leave event before committing to a hide.
# Prevents blinking when the cursor briefly crosses a child widget boundary.
_LEAVE_GUARD_MS = 40


class DropOverlay(QWidget):
    """Semi-transparent overlay shown while the user drags an Excel file.

    Design contract
    ---------------
    * ``show_overlay()`` — call from ``dragEnterEvent``.
    * ``hide_overlay()`` — call from ``dragLeaveEvent`` **and** ``dropEvent``
      (both valid and invalid drops).
    * ``refit()``        — call from the parent's ``resizeEvent``.

    The finished signal of the internal animation is connected **once** in
    ``__init__`` to a stable slot.  The slot decides at runtime whether to
    call ``hide()`` based on a flag, so there is never a risk of duplicate
    connections or missed disconnects.
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Tracks the intended direction of the current/last animation.
        # True  → we are fading OUT and should call hide() on finish.
        # False → we are fading IN; do nothing on finish.
        self._fading_out: bool = False

        self._opacity: float = 0.0
        self.hide()

        # Single animation object reused for both directions.
        self._anim = QPropertyAnimation(self, b"opacity", self)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutSine)

        # Connect finished ONCE here.  The slot checks self._fading_out.
        self._anim.finished.connect(self._on_animation_finished)

        # Anti-flicker guard
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.setInterval(_LEAVE_GUARD_MS)
        self._hide_timer.timeout.connect(self._commit_hide)

        self.refit()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def refit(self) -> None:
        """Resize the overlay to fill the parent widget exactly."""
        if self.parent() and isinstance(self.parent(), QWidget):
            self.setGeometry(self.parent().rect())

    def show_overlay(self) -> None:
        """Fade the overlay in.  Safe to call while already visible."""
        self._hide_timer.stop()
        self._fading_out = False

        if not self.isVisible():
            self.raise_()
            self.show()

        self._animate_to(1.0, _FADE_IN_MS)

    def hide_overlay(self) -> None:
        """Trigger the anti-flicker guard; the overlay fades out if still outside."""
        self._hide_timer.start()

    def force_hide(self) -> None:
        """Immediately stop all animations and hide the overlay without fading.

        Use this as an emergency reset if the state becomes inconsistent.
        """
        self._hide_timer.stop()
        self._anim.stop()
        self._fading_out = False
        self._opacity = 0.0
        self.hide()

    # ------------------------------------------------------------------
    # Animated opacity property
    # ------------------------------------------------------------------

    def _get_opacity(self) -> float:
        return self._opacity

    def _set_opacity(self, value: float) -> None:
        self._opacity = value
        self.update()

    opacity = Property(float, _get_opacity, _set_opacity)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _animate_to(self, target: float, duration: int) -> None:
        """Drive the opacity animation to *target* over *duration* ms."""
        self._anim.stop()
        self._anim.setDuration(duration)
        self._anim.setStartValue(self._opacity)
        self._anim.setEndValue(target)
        self._anim.start()

    def _commit_hide(self) -> None:
        """Called when the anti-flicker timer fires.

        Checks whether the cursor is still inside the parent.  If it is, the
        drag re-entered the window and we keep the overlay visible.  Otherwise
        we start the fade-out animation.
        """
        parent = self.parent()
        if isinstance(parent, QWidget):
            local_pos = parent.mapFromGlobal(QCursor.pos())
            if parent.rect().contains(local_pos):
                return  # cursor re-entered — stay visible

        # Start fade-out; _on_animation_finished will call hide()
        self._fading_out = True
        self._animate_to(0.0, _FADE_OUT_MS)

    def _on_animation_finished(self) -> None:
        """Single, permanent slot wired to QPropertyAnimation.finished.

        Calls hide() only when a fade-out just completed.  This is the only
        place hide() is called after an animation, so there is no risk of
        double-hide or residual dark overlays.
        """
        if self._fading_out:
            self._fading_out = False
            self._opacity = 0.0
            self.hide()

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: ANN001
        """Draw backdrop → dashed card → Excel icon → instructional text."""
        if self._opacity <= 0.0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self._opacity)

        self._draw_backdrop(painter)
        card_rect = self._card_rect()
        self._draw_card(painter, card_rect)
        self._draw_icon(painter, card_rect)
        self._draw_text(painter, card_rect)

        painter.end()

    def _draw_backdrop(self, painter: QPainter) -> None:
        painter.fillRect(self.rect(), _BG_COLOR)

    def _card_rect(self) -> QRect:
        return self.rect().adjusted(
            _CARD_PADDING, _CARD_PADDING, -_CARD_PADDING, -_CARD_PADDING
        )

    def _draw_card(self, painter: QPainter, card_rect: QRect) -> None:
        path = QPainterPath()
        path.addRoundedRect(
            card_rect.adjusted(1, 1, -1, -1),
            _BORDER_RADIUS,
            _BORDER_RADIUS,
        )
        pen = QPen(_BORDER_COLOR_ALPHA, _BORDER_WIDTH)
        pen.setStyle(Qt.PenStyle.CustomDashLine)
        pen.setDashPattern(_DASH_PATTERN)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

    def _draw_icon(self, painter: QPainter, card_rect: QRect) -> None:
        icon_size = min(card_rect.width(), card_rect.height()) // 5
        icon_size = max(48, min(icon_size, 96))
        icon_x = card_rect.center().x() - icon_size // 2
        icon_y = card_rect.top() + int(card_rect.height() * 0.18)
        self._draw_excel_icon(painter, QRect(icon_x, icon_y, icon_size, icon_size))

    def _draw_excel_icon(self, painter: QPainter, rect: QRect) -> None:
        painter.save()
        painter.translate(rect.topLeft())
        w, h = rect.width(), rect.height()

        # Document body
        painter.setBrush(QColor(52, 199, 89, 230))
        painter.setPen(Qt.PenStyle.NoPen)
        fold = int(w * 0.28)
        body = QPainterPath()
        body.moveTo(fold, 0)
        body.lineTo(w, 0)
        body.lineTo(w, h)
        body.lineTo(0, h)
        body.lineTo(0, fold)
        body.closeSubpath()
        painter.drawPath(body)

        # Folded corner
        painter.setBrush(QColor(30, 160, 60, 200))
        corner = QPainterPath()
        corner.moveTo(0, fold)
        corner.lineTo(fold, 0)
        corner.lineTo(fold, fold)
        corner.closeSubpath()
        painter.drawPath(corner)

        # "X" letter
        painter.setFont(QFont("Arial", int(h * 0.30), QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255, 240))
        painter.drawText(
            QRect(0, int(h * 0.30), w, int(h * 0.60)),
            Qt.AlignmentFlag.AlignCenter,
            "X",
        )
        painter.restore()

    def _draw_text(self, painter: QPainter, card_rect: QRect) -> None:
        title_y = card_rect.top() + int(card_rect.height() * 0.55)

        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.setPen(_TITLE_COLOR)
        painter.drawText(
            QRect(card_rect.left(), title_y, card_rect.width(), 30),
            Qt.AlignmentFlag.AlignHCenter,
            "Drop your Excel file here",
        )

        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(_SUBTITLE_COLOR)
        painter.drawText(
            QRect(card_rect.left(), title_y + 36, card_rect.width(), 22),
            Qt.AlignmentFlag.AlignHCenter,
            "Supports .xlsx and .xls",
        )
