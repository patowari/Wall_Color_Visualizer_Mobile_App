import os
import cv2
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.slider import Slider
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.logger import Logger
from android.permissions import request_permissions, Permission
from android.storage import primary_external_storage_path
import plyer


class WallColorVisualizerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = None
        self.original_image = None
        self.processed_image = None
        self.wall_mask = None
        self.selected_color = (255, 255, 255)  # Default white
        
    def build(self):
        # Request necessary permissions
        request_permissions([
            Permission.CAMERA,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE
        ])
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text='Wall Color Visualizer',
            size_hint_y=None,
            height='48dp',
            font_size='20sp'
        )
        main_layout.add_widget(title)
        
        # Image display
        self.image_widget = Image(
            source='',
            size_hint=(1, 0.6),
            allow_stretch=True,
            keep_ratio=True
        )
        main_layout.add_widget(self.image_widget)
        
        # Control buttons layout
        controls_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing=5)
        
        # Camera button
        camera_btn = Button(text='Open Camera')
        camera_btn.bind(on_press=self.open_camera)
        controls_layout.add_widget(camera_btn)
        
        # Gallery button
        gallery_btn = Button(text='From Gallery')
        gallery_btn.bind(on_press=self.open_gallery)
        controls_layout.add_widget(gallery_btn)
        
        # Color picker button
        color_btn = Button(text='Pick Color')
        color_btn.bind(on_press=self.open_color_picker)
        controls_layout.add_widget(color_btn)
        
        main_layout.add_widget(controls_layout)
        
        # Process controls
        process_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing=5)
        
        # Detect wall button
        detect_btn = Button(text='Detect Wall')
        detect_btn.bind(on_press=self.detect_wall)
        process_layout.add_widget(detect_btn)
        
        # Apply color button
        apply_btn = Button(text='Apply Color')
        apply_btn.bind(on_press=self.apply_color)
        process_layout.add_widget(apply_btn)
        
        main_layout.add_widget(process_layout)
        
        # Save/Share controls
        save_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing=5)
        
        # Save button
        save_btn = Button(text='Save Image')
        save_btn.bind(on_press=self.save_image)
        save_layout.add_widget(save_btn)
        
        # Share button
        share_btn = Button(text='Share')
        share_btn.bind(on_press=self.share_image)
        save_layout.add_widget(share_btn)
        
        main_layout.add_widget(save_layout)
        
        # Blend intensity slider
        slider_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
        slider_label = Label(text='Blend:', size_hint_x=None, width='60dp')
        self.blend_slider = Slider(min=0.1, max=1.0, value=0.7, step=0.1)
        slider_layout.add_widget(slider_label)
        slider_layout.add_widget(self.blend_slider)
        main_layout.add_widget(slider_layout)
        
        return main_layout
    
    def open_camera(self, instance):
        """Open camera to capture image"""
        try:
            from kivy.uix.camera import Camera
            
            # Create camera popup
            camera_layout = BoxLayout(orientation='vertical')
            
            # Camera widget
            self.camera = Camera(play=True, resolution=(640, 480))
            camera_layout.add_widget(self.camera)
            
            # Capture button
            capture_layout = BoxLayout(size_hint_y=None, height='50dp', spacing=10)
            capture_btn = Button(text='Capture')
            capture_btn.bind(on_press=self.capture_image)
            cancel_btn = Button(text='Cancel')
            
            capture_layout.add_widget(capture_btn)
            capture_layout.add_widget(cancel_btn)
            camera_layout.add_widget(capture_layout)
            
            # Create popup
            self.camera_popup = Popup(
                title='Camera',
                content=camera_layout,
                size_hint=(0.9, 0.9)
            )
            
            cancel_btn.bind(on_press=self.camera_popup.dismiss)
            self.camera_popup.open()
            
        except Exception as e:
            Logger.error(f"Camera error: {e}")
            self.show_error("Camera not available")
    
    def capture_image(self, instance):
        """Capture image from camera"""
        if self.camera:
            # Export camera image
            temp_path = os.path.join(primary_external_storage_path(), 'temp_capture.png')
            self.camera.export_to_png(temp_path)
            
            # Load captured image
            self.load_image(temp_path)
            self.camera_popup.dismiss()
    
    def open_gallery(self, instance):
        """Open gallery to select image"""
        try:
            # Create file chooser popup
            file_chooser = FileChooserIconView(
                path=primary_external_storage_path(),
                filters=['*.png', '*.jpg', '*.jpeg']
            )
            
            gallery_layout = BoxLayout(orientation='vertical')
            gallery_layout.add_widget(file_chooser)
            
            # Buttons
            btn_layout = BoxLayout(size_hint_y=None, height='50dp', spacing=10)
            select_btn = Button(text='Select')
            cancel_btn = Button(text='Cancel')
            
            btn_layout.add_widget(select_btn)
            btn_layout.add_widget(cancel_btn)
            gallery_layout.add_widget(btn_layout)
            
            # Create popup
            self.gallery_popup = Popup(
                title='Select Image',
                content=gallery_layout,
                size_hint=(0.9, 0.9)
            )
            
            def select_image(instance):
                if file_chooser.selection:
                    self.load_image(file_chooser.selection[0])
                    self.gallery_popup.dismiss()
            
            select_btn.bind(on_press=select_image)
            cancel_btn.bind(on_press=self.gallery_popup.dismiss)
            self.gallery_popup.open()
            
        except Exception as e:
            Logger.error(f"Gallery error: {e}")
            self.show_error("Could not open gallery")
    
    def load_image(self, image_path):
        """Load image from path"""
        try:
            # Load with OpenCV
            self.original_image = cv2.imread(image_path)
            if self.original_image is not None:
                # Convert BGR to RGB for display
                rgb_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
                self.display_image(rgb_image)
                Logger.info(f"Image loaded: {image_path}")
            else:
                self.show_error("Could not load image")
        except Exception as e:
            Logger.error(f"Load image error: {e}")
            self.show_error("Error loading image")
    
    def display_image(self, cv_image):
        """Display OpenCV image in Kivy Image widget"""
        try:
            # Resize for display
            height, width = cv_image.shape[:2]
            if width > 800:
                scale = 800 / width
                new_width = 800
                new_height = int(height * scale)
                cv_image = cv2.resize(cv_image, (new_width, new_height))
            
            # Convert to texture
            buf = cv_image.tobytes()
            texture = Texture.create(size=(cv_image.shape[1], cv_image.shape[0]))
            texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            texture.flip_vertical()
            
            # Update image widget
            self.image_widget.texture = texture
            
        except Exception as e:
            Logger.error(f"Display image error: {e}")
    
    def open_color_picker(self, instance):
        """Open color picker dialog"""
        color_picker = ColorPicker()
        
        picker_layout = BoxLayout(orientation='vertical')
        picker_layout.add_widget(color_picker)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=None, height='50dp', spacing=10)
        select_btn = Button(text='Select Color')
        cancel_btn = Button(text='Cancel')
        
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        picker_layout.add_widget(btn_layout)
        
        # Create popup
        self.color_popup = Popup(
            title='Pick Color',
            content=picker_layout,
            size_hint=(0.8, 0.8)
        )
        
        def select_color(instance):
            # Convert from 0-1 range to 0-255
            r, g, b, a = color_picker.color
            self.selected_color = (int(b*255), int(g*255), int(r*255))  # BGR format for OpenCV
            Logger.info(f"Selected color: {self.selected_color}")
            self.color_popup.dismiss()
        
        select_btn.bind(on_press=select_color)
        cancel_btn.bind(on_press=self.color_popup.dismiss)
        self.color_popup.open()
    
    def detect_wall(self, instance):
        """Detect wall regions in the image using OpenCV"""
        if self.original_image is None:
            self.show_error("Please load an image first")
            return
        
        try:
            # Convert to different color spaces for better wall detection
            hsv = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            
            # Method 1: Edge detection + morphology
            edges = cv2.Canny(gray, 50, 150)
            kernel = np.ones((5,5), np.uint8)
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # Method 2: Color-based segmentation (detect light colored walls)
            # Define range for wall colors (typically light colors)
            lower_wall = np.array([0, 0, 100])  # Light colors
            upper_wall = np.array([180, 50, 255])
            wall_mask_color = cv2.inRange(hsv, lower_wall, upper_wall)
            
            # Method 3: Combine both methods
            combined_mask = cv2.bitwise_or(wall_mask_color, cv2.bitwise_not(edges))
            
            # Apply morphological operations to clean up
            kernel = np.ones((7,7), np.uint8)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
            
            # Find largest contour (likely the wall)
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                self.wall_mask = np.zeros(gray.shape, dtype=np.uint8)
                cv2.fillPoly(self.wall_mask, [largest_contour], 255)
            else:
                self.wall_mask = combined_mask
            
            # Display the mask overlay
            mask_overlay = self.original_image.copy()
            mask_overlay[self.wall_mask > 0] = [0, 255, 0]  # Green overlay for detected wall
            
            # Blend original and overlay
            result = cv2.addWeighted(self.original_image, 0.7, mask_overlay, 0.3, 0)
            rgb_result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            self.display_image(rgb_result)
            
            Logger.info("Wall detection completed")
            
        except Exception as e:
            Logger.error(f"Wall detection error: {e}")
            self.show_error("Error detecting wall")
    
    def apply_color(self, instance):
        """Apply selected color to detected wall area"""
        if self.original_image is None:
            self.show_error("Please load an image first")
            return
        if self.wall_mask is None:
            self.show_error("Please detect wall first")
            return
        
        try:
            # Create colored overlay
            color_overlay = np.zeros_like(self.original_image)
            color_overlay[self.wall_mask > 0] = self.selected_color
            
            # Get blend intensity from slider
            blend_intensity = self.blend_slider.value
            
            # Apply color with blending
            result = self.original_image.copy()
            
            # Blend the color only where the wall is detected
            mask_3channel = cv2.merge([self.wall_mask, self.wall_mask, self.wall_mask])
            mask_normalized = mask_3channel.astype(float) / 255
            
            # Apply color with proper blending
            result = result.astype(float)
            color_overlay = color_overlay.astype(float)
            
            # Blend: result = original * (1-alpha) + color * alpha, only where mask exists
            alpha = blend_intensity * mask_normalized
            result = result * (1 - alpha) + color_overlay * alpha
            
            self.processed_image = result.astype(np.uint8)
            
            # Display result
            rgb_result = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
            self.display_image(rgb_result)
            
            Logger.info("Color applied successfully")
            
        except Exception as e:
            Logger.error(f"Apply color error: {e}")
            self.show_error("Error applying color")
    
    def save_image(self, instance):
        """Save the processed image"""
        if self.processed_image is None:
            self.show_error("No processed image to save")
            return
        
        try:
            # Create save path
            save_dir = os.path.join(primary_external_storage_path(), 'WallColorizer')
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # Generate unique filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wall_colored_{timestamp}.jpg"
            save_path = os.path.join(save_dir, filename)
            
            # Save image
            cv2.imwrite(save_path, self.processed_image)
            
            self.show_success(f"Image saved to: {save_path}")
            Logger.info(f"Image saved: {save_path}")
            
        except Exception as e:
            Logger.error(f"Save error: {e}")
            self.show_error("Error saving image")
    
    def share_image(self, instance):
        """Share the processed image"""
        if self.processed_image is None:
            self.show_error("No processed image to share")
            return
        
        try:
            # Save temporary file for sharing
            temp_dir = os.path.join(primary_external_storage_path(), 'temp')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            temp_path = os.path.join(temp_dir, 'wall_colored_share.jpg')
            cv2.imwrite(temp_path, self.processed_image)
            
            # Use plyer to share
            plyer.shareImage(
                filepath=temp_path,
                title="Wall Color Visualization",
                mime_type="image/jpeg"
            )
            
        except Exception as e:
            Logger.error(f"Share error: {e}")
            self.show_error("Error sharing image")
    
    def show_error(self, message):
        """Show error popup"""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def show_success(self, message):
        """Show success popup"""
        popup = Popup(
            title='Success',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()


if __name__ == '__main__':
    WallColorVisualizerApp().run()
