# gui/custom_graphics_view.py
import numpy as np
import cv2
from PyQt5.QtWidgets import QGraphicsView, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsScene
from PyQt5.QtGui import QImage, QPixmap, QColor, QPen, QMouseEvent
from PyQt5.QtCore import Qt, QRectF

class CustomGraphicsView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.brightness = 0
        self.contrast = 1.0
        self.image_item = None  # Reference to QGraphicsPixmapItem
        self.region_selected = False
        self.region_rect_item = None
        self.inner_region_selected = True
        self.region_size = 50  # Default size percentage

    def set_image(self, pixmap: QPixmap):
        """Set the image in the scene and assign it to image_item."""
        if not pixmap or pixmap.isNull():
            print("Invalid pixmap provided.")
            return

        # Clear the scene and add the new pixmap
        self.scene().clear()
        self.image_item = QGraphicsPixmapItem(pixmap)
        self.scene().addItem(self.image_item)
        print("Image set successfully in the scene.")
        

    def draw_region(self):
        """Draw the region rectangle based on the current settings."""
        if not self.image_item:
            return

        if self.region_rect_item:
            self.scene().removeItem(self.region_rect_item)

        scene_rect = self.image_item.boundingRect()
        width = scene_rect.width()
        height = scene_rect.height()

        if self.inner_region_selected:
            rect_width = width * (self.region_size / 100.0)
            rect_height = height * (self.region_size / 100.0)
            rect_x = (width - rect_width) / 2
            rect_y = (height - rect_height) / 2
        else:
            rect_width = width - (width * (self.region_size / 100.0))
            rect_height = height - (height * (self.region_size / 100.0))
            rect_x = (width - rect_width) / 2
            rect_y = (height - rect_height) / 2

        self.region_rect_item = QGraphicsRectItem(QRectF(rect_x, rect_y, rect_width, rect_height))
        self.region_rect_item.setBrush(QColor(100, 100, 255, 100))  # Semi-transparent blue
        self.region_rect_item.setPen(QPen(Qt.NoPen))
        self.scene().addItem(self.region_rect_item)

    def adjust_brightness_contrast(self):
        """Adjust brightness and contrast of the image."""
        if not self.image_item:
            print("No image item found in the scene.")
            return

        pixmap = self.image_item.pixmap()
        if pixmap.isNull():
            print("Pixmap is invalid.")
            return

        # Convert QPixmap to QImage
        image = pixmap.toImage()
        if image.isNull():
            print("QImage is invalid.")
            return

        try:
            # Convert QImage to numpy array
            width, height = image.width(), image.height()
            image = image.convertToFormat(QImage.Format_Grayscale8)
            buffer = image.bits()
            buffer.setsize(image.byteCount())
            array = np.frombuffer(buffer, dtype=np.uint8).reshape((height, width))

            print(f"Image array shape: {array.shape}, dtype: {array.dtype}")

            # Validate brightness and contrast
            if not hasattr(self, "brightness") or not hasattr(self, "contrast"):
                self.brightness = 0
                self.contrast = 1.0
                print("Brightness and contrast set to defaults.")

            if not isinstance(self.brightness, (int, float)) or not isinstance(self.contrast, (int, float)):
                print("Brightness and contrast must be numeric values.")
                return

            # Apply brightness and contrast adjustments
            adjusted = cv2.convertScaleAbs(array, alpha=self.contrast, beta=self.brightness)

            if adjusted is None or adjusted.size == 0:
                print("Adjustment failed, resulting data is invalid.")
                return

            # Convert adjusted numpy array back to QPixmap
            adjusted_image = QImage(adjusted.data, adjusted.shape[1], adjusted.shape[0], QImage.Format_Grayscale8)
            self.image_item.setPixmap(QPixmap.fromImage(adjusted_image))
        except Exception as e:
            print(f"Error adjusting brightness/contrast: {e}")

    def update_region_size(self, size):
        """Update the size of the region rectangle."""
        self.region_size = size
        self.draw_region()
        print(f"Updated region size: {size}%")

    def select_inner_region(self):
        """Select the inner region."""
        self.inner_region_selected = True
        self.draw_region()
        print("Inner region selected.")

    def select_outer_region(self):
        """Select the outer region."""
        self.inner_region_selected = False
        self.draw_region()
        print("Outer region selected.")



    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.last_mouse_position = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.last_mouse_position:
            dx = event.x() - self.last_mouse_position.x()
            dy = event.y() - self.last_mouse_position.y()

            try:
                # Update brightness (vertical movement) and contrast (horizontal movement)
                self.contrast = max(0.1, min(3.0, self.contrast + dx / 100.0))
                self.brightness = max(-100, min(100, self.brightness + dy / 2.0))

                print(f"Brightness: {self.brightness}, Contrast: {self.contrast}")

                # Apply the adjustments
                self.adjust_brightness_contrast()
                self.last_mouse_position = event.pos()
            except Exception as e:
                print(f"Error in brightness/contrast update: {e}")
                return


    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.last_mouse_position = None