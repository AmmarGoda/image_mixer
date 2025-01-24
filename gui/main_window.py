# gui/main_window.py
import numpy as np
import cv2
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QPushButton, QComboBox, QFileDialog, QRadioButton,
    QGraphicsScene, QProgressBar, QGroupBox, QMessageBox, QSlider, QGraphicsView
)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from processing.image_processor import ImageProcessor
from gui.custom_graphics_view import CustomGraphicsView
from utils.theme import apply_dark_theme

class ImageMixerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Mixer")
        self.setGeometry(100, 100, 1400, 900)
        self.combos = []
        self.initUI()
        self.input_images = [None] * 4
        self.fft_components = [None] * 4
        self.output_image = None
        self.processor = None
        apply_dark_theme()
        self.region_size_slider = None  # Slider to adjust region size
        self.region_rect = None  # Store the unified region rectangle
        self.result_views = []
        

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        left_layout = QVBoxLayout()
        top_row_layout = QHBoxLayout()
        self.viewports = []
        self.component_selectors = []

        for i in range(2):  # First two input viewports
            viewport, combo_box = self.create_input_viewport(f"Input View {i + 1}", i)
            self.viewports.append(viewport)
            self.component_selectors.append(combo_box)
            top_row_layout.addWidget(viewport)

        left_layout.addLayout(top_row_layout)

        bottom_row_layout = QHBoxLayout()
        for i in range(2, 4):  # Last two input viewports
            viewport, combo_box = self.create_input_viewport(f"Input View {i + 1}", i)
            self.viewports.append(viewport)
            self.component_selectors.append(combo_box)
            bottom_row_layout.addWidget(viewport)

        left_layout.addLayout(bottom_row_layout)

        right_layout = QVBoxLayout()

        self.output_group = QGroupBox("Output Viewports")
        output_layout = QVBoxLayout(self.output_group)

        self.inner_region_radio = QRadioButton("Inner Region")
        self.inner_region_radio.toggled.connect(self.on_inner_region_selected)
        self.outer_region_radio = QRadioButton("Outer Region")
        self.outer_region_radio.toggled.connect(self.on_outer_region_selected)

        self.region_size_slider = QSlider(Qt.Horizontal)
        self.region_size_slider.setMinimum(0)
        self.region_size_slider.setMaximum(100)
        self.region_size_slider.setValue(50)
        self.region_size_slider.setObjectName("region_size_slider")
        self.region_size_slider.valueChanged.connect(self.update_region_size)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        output_layout.addWidget(self.inner_region_radio)
        output_layout.addWidget(self.outer_region_radio)
        output_layout.addWidget(self.region_size_slider)
        output_layout.addWidget(self.progress_bar)


        self.mode = QComboBox()
        self.mode.addItems(["Select Mode","Magnitude and Phase" , "Real and Imaginary"])
        output_layout.addWidget(self.mode)
        self.mode.currentIndexChanged.connect(self.update_modes)

        self.output_viewports = []
        for i in range(2):
            output_viewport, result_view = self.create_output_viewport(f"Output View {i + 1}")
            self.output_viewports.append(output_viewport)
            output_layout.addWidget(output_viewport)

        output_controls = self.create_output_controls()
        output_layout.addWidget(output_controls)

        right_layout.addWidget(self.output_group)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

    

    def on_inner_region_selected(self):
        for viewport in self.viewports:
            graphics_view = viewport.findChild(CustomGraphicsView)
            if graphics_view:
                graphics_view.select_inner_region()

    def on_outer_region_selected(self):
        for viewport in self.viewports:
            graphics_view = viewport.findChild(CustomGraphicsView)
            if graphics_view:
                graphics_view.select_outer_region()

    def update_region_size(self, value):
        for viewport in self.viewports:
            graphics_view = viewport.findChild(CustomGraphicsView)
            if graphics_view:
                graphics_view.update_region_size(value)


    def create_input_viewport(self, title, input_index):
        viewport_widget = QWidget()
        layout = QVBoxLayout(viewport_widget)

        title_label = QLabel(title)

        original_scene = QGraphicsScene()
        original_view = CustomGraphicsView(original_scene)
        original_view.setObjectName(f"original_view_{input_index}")  # Assign unique object name for reference
        original_scene.mouseDoubleClickEvent = lambda event: self.load_image(original_view, input_index)

        component_scene = QGraphicsScene()
        component_view = CustomGraphicsView(component_scene)
        component_view.setObjectName(f"component_view_{input_index}")  # Assign unique object name for reference

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(1) 
        slider.setMaximum(100) 
        slider.setValue(1) # Default value 
        slider.setObjectName(f"weight_slider_{input_index}")

        combo_box = QComboBox()
        combo_box.addItems(["Select Component", "FT Magnitude", "FT Phase", "FT Real", "FT Imaginary"])
        combo_box.currentIndexChanged.connect(lambda _, idx=input_index : self.update_component_display(idx))  # Pass input index
        self.combos.append(combo_box)

        layout.addWidget(title_label)
        layout.addWidget(QLabel("Original Image:"))
        layout.addWidget(original_view)
        layout.addWidget(QLabel("Fourier Component:"))
        layout.addWidget(component_view)
        layout.addWidget(slider)
        layout.addWidget(combo_box)

        return viewport_widget, combo_box

    def update_modes(self):
        """Enable or disable dropdown items based on the selected mode."""
        selected_mode = self.mode.currentText()  # Get the selected mode

        if selected_mode == "Magnitude and Phase":
            for combo in self.combos:  # self.combos contains all the dropdowns
                combo.model().item(1).setEnabled(True)   # Enable "Magnitude"
                combo.model().item(2).setEnabled(True)   # Enable "Phase"
                combo.model().item(3).setEnabled(False)  # Disable "Real"
                combo.model().item(4).setEnabled(False)  # Disable "Imaginary"

        elif selected_mode == "Real and Imaginary":
            for combo in self.combos:
                combo.model().item(1).setEnabled(False)  # Disable "Magnitude"
                combo.model().item(2).setEnabled(False)  # Disable "Phase"
                combo.model().item(3).setEnabled(True)   # Enable "Real"
                combo.model().item(4).setEnabled(True)   # Enable "Imaginary"


    
    def update_component_display(self, input_index):
        try:
            selected_component = self.component_selectors[input_index].currentText()
            
            image = self.input_images[input_index]

            if image is None:
                print(f"No image loaded for input {input_index + 1}.")
                return

            fft = np.fft.fft2(image)
            fft_shift = np.fft.fftshift(fft)

            if selected_component == "FT Magnitude":
                component = np.log(np.abs(fft_shift) + 1)  # Log scale for better visualization
            elif selected_component == "FT Phase":
                component = np.angle(fft_shift)
            elif selected_component == "FT Real":
                component = np.real(fft_shift)
            elif selected_component == "FT Imaginary":
                component = np.imag(fft_shift)
            else:
                print(f"Invalid component selected: {selected_component}")
                return

            

            # Normalize component to displayable range (0-255)
            normalized_component = cv2.normalize(component, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

            # Update the Fourier Component View
            component_view = self.viewports[input_index].findChild(QGraphicsView, f"component_view_{input_index}")
            if component_view is not None:
                scene = QGraphicsScene()
                height, width = normalized_component.shape
                bytes_per_line = width
                qimage = QImage(normalized_component.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
                pixmap = QPixmap.fromImage(qimage)

                # Scale the pixmap to fit the viewport, maintaining aspect ratio
                viewport_size = component_view.size()
                scaled_pixmap = pixmap.scaled(
                    viewport_size.width(),
                    viewport_size.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                scene.addPixmap(scaled_pixmap)
                component_view.setScene(scene)
            else:
                print(f"Fourier Component View not found for input {input_index + 1}.")
        except Exception as e:
            print(f"Error updating component display: {e}")

    def load_image(self, viewport, input_index):
        
        try:
            path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.bmp)")
            if path:
                print(f"Selected image path: {path}")
                image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                #self.update_component_display(input_index , "FT Magnitude")
                
                if image is None:
                    print(f"Failed to load image: {path}")
                else:
                    print(f"Image loaded successfully: {path}")
                    self.input_images[input_index] = image
                    self.display_image(image, viewport)


                    
            else:
                print("No image selected.")
        except Exception as e:
            print(f"An error occurred while loading the image: {e}")

    def display_image(self, image, viewport):
        try:
            if image is not None and image.size >0:
                print(f"Displaying image of shape: {image.shape}")

                # Convert image to QPixmap
                height, width = image.shape
                bytes_per_line = width
                qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
                pixmap = QPixmap.fromImage(qimage)


                # Resize the pixmap to fit the viewport, keeping aspect ratio
                viewport_size = viewport.size()
                scaled_pixmap = pixmap.scaled(
                    viewport_size.width(),
                    viewport_size.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                # Display the scaled pixmap using CustomGraphicsView's set_image
                if isinstance(viewport, CustomGraphicsView):
                    viewport.set_image(scaled_pixmap)
                else:
                    print("Viewport is not a CustomGraphicsView instance.")

                
            else:
                print("No image to display.")
        except Exception as e:  
            print(f"An error occurred while displaying the image: {e}")

    def create_output_viewport(self, title):
        output_widget = QWidget()
        layout = QVBoxLayout(output_widget)

        title_label = QLabel(title)
        result_scene = QGraphicsScene()

        result_view = CustomGraphicsView(result_scene)

        layout.addWidget(title_label)
        layout.addWidget(QLabel("Mixed Image Result:"))
        layout.addWidget(result_view)

        return output_widget, result_view

    def create_output_controls(self):
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)

        self.select_output_view_combo = QComboBox()
        self.select_output_view_combo.addItems(["Select Output View", "Output View 1", "Output View 2"])

        self.start_mixing_button = QPushButton("Start Mixing")
        self.start_mixing_button.clicked.connect(self.start_mixing)

        control_layout.addWidget(QLabel("Select which output viewport to display result:"))
        control_layout.addWidget(self.select_output_view_combo)
        control_layout.addWidget(self.start_mixing_button)

        return control_widget
    
    def start_mixing(self):
        try:
            # Filter out None images
            valid_images = [image for image in self.input_images if image is not None]
            if not valid_images:
                print("No valid input images available.")
                QMessageBox.warning(self, "Input Error", "Please load at least one input image before starting the mixing process.")
                return

            # Get selected components and region
            components = [selector.currentText() if self.input_images[idx] is not None else "None" for idx, selector in enumerate(self.component_selectors)]
            components = [comp for comp in components if comp != "None"]
            region = "Inner" if self.inner_region_radio.isChecked() else "Outer"

            # Get weights from sliders
            weights = []
            for i in range(4):  # Assuming 4 input viewports
                slider = self.findChild(QSlider, f"weight_slider_{i}")
                if slider:
                    print(f"Slider {i} value: {slider.value()}")
                    weights.append(slider.value() / 100.0)  # Normalize to range 0.0 - 1.0
                else:
                    print(f"Slider {i} not found.")
                    weights.append(0.0)  # Default to 0 if no slider is found

            # Filter weights for valid images
            weights = [weights[i] for i in range(4) if self.input_images[i] is not None]

            # Get region size from the slider
            region_size_slider = self.findChild(QSlider, "region_size_slider")
            if region_size_slider:
                region_size = region_size_slider.value()
                print(f"Region size: {region_size}")
            else:
                print("Region size slider not found.")
                region_size = 50  # Default to 50 if slider is not found

            # Cancel the previous task if any is running
            if self.processor and self.processor.isRunning():
                self.processor.running = False
                self.processor.wait()

            # Start a new processing task with region_size
            print(f"Starting ImageProcessor with weights: {weights} and region size: {region_size}")
            self.processor = ImageProcessor(valid_images, components, region, weights, region_size)
            self.processor.progress.connect(self.update_progress)
            self.processor.result.connect(self.display_result)
            self.processor.start()
        except Exception as e:
            print(f"Error starting the mixing process: {e}")


    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_result(self, image):
        if image is not None and image.size > 1:  # Ensure the image is valid and larger than a minimal placeholder
            print(f"Displaying image with shape: {image.shape}")
            self.output_image = image
            selected_output = self.select_output_view_combo.currentText()
            
            if selected_output == "Output View 1":
                result_view = self.output_viewports[0]  # Use the stored reference to the first output viewport
                if result_view:
                    self.display_image(image, result_view.findChild(CustomGraphicsView))
                    print("Image displayed in Output View 1.")
                else:
                    print("Result view not found for Output View 1.")
            elif selected_output == "Output View 2":
                result_view = self.output_viewports[1]  # Use the stored reference to the second output viewport
                if result_view:
                    self.display_image(image, result_view.findChild(CustomGraphicsView))
                    print("Image displayed in Output View 2.")
                else:
                    print("Result view not found for Output View 2.")
        else:
            print("Received invalid image or image is too small to display.")

