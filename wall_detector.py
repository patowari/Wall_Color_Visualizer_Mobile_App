import cv2
import numpy as np
from sklearn.cluster import KMeans
import logging

class WallDetector:
    """Advanced wall detection using multiple computer vision techniques"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def detect_wall_advanced(self, image, method='combined'):
        """
        Detect wall regions using various methods
        
        Args:
            image: Input image in BGR format
            method: Detection method ('edge', 'color', 'texture', 'combined')
        
        Returns:
            Binary mask of detected wall regions
        """
        try:
            if method == 'edge':
                return self._edge_based_detection(image)
            elif method == 'color':
                return self._color_based_detection(image)
            elif method == 'texture':
                return self._texture_based_detection(image)
            elif method == 'combined':
                return self._combined_detection(image)
            else:
                return self._combined_detection(image)
        except Exception as e:
            self.logger.error(f"Wall detection error: {e}")
            return None
    
    def _edge_based_detection(self, image):
        """Detect walls using edge detection and morphological operations"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection with different thresholds
        edges1 = cv2.Canny(blurred, 50, 150)
        edges2 = cv2.Canny(blurred, 100, 200)
        
        # Combine edges
        edges = cv2.bitwise_or(edges1, edges2)
        
        # Morphological operations to fill gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # Fill enclosed regions
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask = np.zeros(gray.shape, dtype=np.uint8)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Filter small contours
                cv2.fillPoly(mask, [contour], 255)
        
        return mask
    
    def _color_based_detection(self, image):
        """Detect walls based on color characteristics"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define multiple color ranges for typical wall colors
        wall_ranges = [
            # Light colors (white, cream, light gray)
            ([0, 0, 150], [180, 30, 255]),
            # Beige/tan colors
            ([10, 20, 100], [25, 100, 200]),
            # Light blue/gray
            ([90, 10, 120], [130, 50, 200])
        ]
        
        combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        for lower, upper in wall_ranges:
            lower = np.array(lower)
            upper = np.array(upper)
            mask = cv2.inRange(hsv, lower, upper)
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        # Clean up the mask
        kernel = np.ones((7, 7), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        
        return combined_mask
    
    def _texture_based_detection(self, image):
        """Detect walls based on texture analysis"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate texture features using Local Binary Pattern approach
        # Simplified version using standard deviation in local windows
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (9, 9), 0)
        
        # Calculate local standard deviation
        kernel = np.ones((15, 15), np.float32) / 225
        mean = cv2.filter2D(blurred.astype(np.float32), -1, kernel)
        sqr_diff = (blurred.astype(np.float32) - mean) ** 2
        std = np.sqrt(cv2.filter2D(sqr_diff, -1, kernel))
        
        # Walls typically have low texture (low standard deviation)
        wall_mask = (std < np.percentile(std, 30)).astype(np.uint8) * 255
        
        # Clean up
        kernel = np.ones((7, 7), np.uint8)
        wall_mask = cv2.morphologyEx(wall_mask, cv2.MORPH_CLOSE, kernel)
        
        return wall_mask
    
    def _combined_detection(self, image):
        """Combine multiple detection methods for robust wall detection"""
        # Get results from different methods
        edge_mask = self._edge_based_detection(image)
        color_mask = self._color_based_detection(image)
        texture_mask = self._texture_based_detection(image)
        
        # Combine masks with weighted voting
        h, w = image.shape[:2]
        combined = np.zeros((h, w), dtype=np.float32)
        
        # Weight the different methods
        if edge_mask is not None:
            combined += (edge_mask.astype(np.float32) / 255) * 0.3
        if color_mask is not None:
            combined += (color_mask.astype(np.float32) / 255) * 0.4
        if texture_mask is not None:
            combined += (texture_mask.astype(np.float32) / 255) * 0.3
        
        # Threshold the combined result
        final_mask = (combined > 0.5).astype(np.uint8) * 255
        
        # Post-processing: find largest connected component
        contours, _ = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get the largest contour (most likely the wall)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Create clean mask
            clean_mask = np.zeros_like(final_mask)
            cv2.fillPoly(clean_mask, [largest_contour], 255)
            
            # Apply morphological smoothing
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            clean_mask = cv2.morphologyEx(clean_mask, cv2.MORPH_CLOSE, kernel)
            clean_mask = cv2.morphologyEx(clean_mask, cv2.MORPH_OPEN, kernel)
            
            return clean_mask
        
        return final_mask
    
    def refine_mask_interactive(self, image, initial_mask, seed_points=None):
        """
        Refine wall mask using interactive techniques like GrabCut
        
        Args:
            image: Original image
            initial_mask: Initial wall detection mask
            seed_points: Optional list of seed points for refinement
        
        Returns:
            Refined mask
        """
        try:
            # Convert initial mask to GrabCut format
            gc_mask = np.zeros(initial_mask.shape[:2], dtype=np.uint8)
            gc_mask[initial_mask == 255] = cv2.GC_PR_FGD  # Probable foreground
            gc_mask[initial_mask == 0] = cv2.GC_PR_BGD    # Probable background
            
            # Initialize models
            bgd_model = np.zeros((1, 65), np.float64)
            fgd_model = np.zeros((1, 65), np.float64)
            
            # Apply GrabCut
            cv2.grabCut(image, gc_mask, None, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_MASK)
            
            # Extract foreground
            refined_mask = np.where((gc_mask == 2) | (gc_mask == 0), 0, 255).astype(np.uint8)
            
            return refined_mask
            
        except Exception as e:
            self.logger.error(f"Mask refinement error: {e}")
            return initial_mask
    
    def detect_wall_segments(self, image, mask):
        """
        Segment the detected wall into different regions/planes
        
        Args:
            image: Original image
            mask: Wall detection mask
        
        Returns:
            Dictionary with segmented wall regions
        """
        try:
            # Extract wall region
            wall_region = cv2.bitwise_and(image, image, mask=mask)
            
            # Convert to LAB color space for better clustering
            lab_image = cv2.cvtColor(wall_region, cv2.COLOR_BGR2LAB)
            
            # Get only wall pixels
            wall_pixels = lab_image[mask > 0]
            
            if len(wall_pixels) == 0:
                return {'segments': [], 'mask': mask}
            
            # Perform K-means clustering to segment different wall planes
            n_clusters = min(3, len(wall_pixels) // 100)  # Adaptive number of clusters
            if n_clusters < 2:
                return {'segments': [mask], 'mask': mask}
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(wall_pixels)
            
            # Create segment masks
            segments = []
            label_mask = np.zeros(mask.shape, dtype=np.int32)
            label_mask[mask > 0] = labels
            
            for i in range(n_clusters):
                segment_mask = (label_mask == i).astype(np.uint8) * 255
                
                # Clean up small segments
                contours, _ = cv2.findContours(segment_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                clean_segment = np.zeros_like(segment_mask)
                
                for contour in contours:
                    if cv2.contourArea(contour) > 500:  # Minimum segment size
                        cv2.fillPoly(clean_segment, [contour], 255)
                
                if np.sum(clean_segment) > 0:
                    segments.append(clean_segment)
            
            return {'segments': segments, 'mask': mask}
            
        except Exception as e:
            self.logger.error(f"Wall segmentation error: {e}")
            return {'segments': [mask], 'mask': mask}
    
    def estimate_wall_lighting(self, image, mask):
        """
        Estimate lighting conditions on the wall for better color application
        
        Args:
            image: Original image
            mask: Wall mask
        
        Returns:
            Lighting map for the wall
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to get lighting estimation
            lighting = cv2.GaussianBlur(gray, (51, 51), 0)
            
            # Normalize lighting
            lighting_norm = cv2.normalize(lighting, None, 0, 255, cv2.NORM_MINMAX)
            
            # Apply mask
            wall_lighting = np.zeros_like(lighting_norm)
            wall_lighting[mask > 0] = lighting_norm[mask > 0]
            
            return wall_lighting
            
        except Exception as e:
            self.logger.error(f"Lighting estimation error: {e}")
            return np.ones_like(mask) * 128  # Default medium lighting
