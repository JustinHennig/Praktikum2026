# Header panel with purple-to-black gradient, logo, app title, and dark/light mode toggle.

import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, QSize, QRect, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QPainterPath, QBrush, QPen
from PySide6.QtSvgWidgets import QSvgWidget

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets")
LOGO = os.path.join(ASSETS_DIR, "planqc_logo.svg")


class _ToggleSwitch(QWidget):
    """Animated pill-shaped toggle switch (dark ↔ light)."""
    toggled = Signal(bool)  # emits True when switched to light mode

    _TRACK_W = 52
    _TRACK_H = 26
    _KNOB_D  = 20

    def __init__(self, parent=None):
        super().__init__(parent)
        self._checked = False          # False = dark mode
        self._knob_x  = 3.0           # animated x position of knob
        self.setFixedSize(self._TRACK_W, self._TRACK_H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._anim = QPropertyAnimation(self, b"knob_x", self)
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

    # ── Qt property for animation ──────────────────
    def _get_knob_x(self):
        return self._knob_x

    def _set_knob_x(self, value):
        self._knob_x = value
        self.update()

    knob_x = Property(float, _get_knob_x, _set_knob_x)

    # ── Public helpers ──────────────────────────────
    @property
    def is_light(self) -> bool:
        return self._checked

    def set_checked(self, value: bool, *, animate: bool = True):
        if self._checked == value:
            return
        self._checked = value
        end_x = self._TRACK_W - self._KNOB_D - 3 if value else 3
        if animate:
            self._anim.setStartValue(self._knob_x)
            self._anim.setEndValue(float(end_x))
            self._anim.start()
        else:
            self._knob_x = float(end_x)
            self.update()

    # ── Mouse interaction ───────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._checked = not self._checked
            end_x = self._TRACK_W - self._KNOB_D - 3 if self._checked else 3
            self._anim.setStartValue(self._knob_x)
            self._anim.setEndValue(float(end_x))
            self._anim.start()
            self.toggled.emit(self._checked)

    # ── Painting ────────────────────────────────────
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Track
        track_color = QColor("#7040C0") if self._checked else QColor("#3a3a5a")
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(track_color))
        radius = self._TRACK_H / 2
        p.drawRoundedRect(0, 0, self._TRACK_W, self._TRACK_H, radius, radius)

        # Knob
        knob_y = (self._TRACK_H - self._KNOB_D) / 2
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("#ffffff")))
        p.drawEllipse(int(self._knob_x), int(knob_y), self._KNOB_D, self._KNOB_D)
        p.end()


class HeaderPanel(QWidget):
    """App header: purple→black gradient | logo | title | theme toggle."""
    theme_changed = Signal(bool)  # True = light mode

    HEIGHT = 64

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(self.HEIGHT)
        self._is_light = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(14)

        # ── Logo ──────────────────────────────────────
        # Preserve aspect ratio: the SVG viewBox is ~425 x 142 → ratio ≈ 2.995
        _LOGO_H = 40
        _LOGO_W = round(_LOGO_H * (425.1968384 / 141.7323303))
        self._logo = QSvgWidget(LOGO, self)
        self._logo.setFixedSize(QSize(_LOGO_W, _LOGO_H))
        self._logo.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._logo.setStyleSheet("background: transparent;")

        # ── Title ─────────────────────────────────────
        self._title = QLabel("SCPI Measurement Application")
        self._title.setStyleSheet(
            "color: #ffffff; font-size: 17px; font-weight: bold; "
            "font-family: 'Segoe UI'; background: transparent;"
        )
        self._title.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)

        # ── Toggle area ───────────────────────────────
        toggle_container = QWidget()
        toggle_container.setStyleSheet("background: transparent;")
        t_layout = QHBoxLayout(toggle_container)
        t_layout.setContentsMargins(0, 0, 0, 0)
        t_layout.setSpacing(8)

        self._toggle_label = QLabel("Dark")
        self._toggle_label.setStyleSheet(
            "color: rgba(255,255,255,200); font-size: 12px; background: transparent;"
        )
        self._toggle = _ToggleSwitch()
        self._toggle.toggled.connect(self._on_toggle)

        t_layout.addWidget(self._toggle_label)
        t_layout.addWidget(self._toggle)

        layout.addWidget(self._logo, 1, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._title, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(toggle_container, 1, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)

    # ── Gradient background ────────────────────────
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0, QColor("#3A1060"))
        grad.setColorAt(0.5, QColor("#1E0840"))
        grad.setColorAt(1.0, QColor("#060010"))
        p.fillRect(self.rect(), QBrush(grad))
        p.end()

    # ── Toggle handler ─────────────────────────────
    def _on_toggle(self, is_light: bool):
        self._is_light = is_light
        self._toggle_label.setText("Light" if is_light else "Dark")
        self.theme_changed.emit(is_light)
