import cv2
import numpy as np
import sys
import os

def main():
    if len(sys.argv) != 3:
        print("Usage: python image_feature_matching.py <image1> <image2>")
        sys.exit(1)
    
    img1_path = sys.argv[1]
    img2_path = sys.argv[2]
    
    # Load images
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    
    if img1 is None or img2 is None:
        print("Error: Could not load one or both images")
        sys.exit(1)
    
    # Initialize ORB detector with better spatial distribution
    orb = cv2.ORB_create(
        nfeatures=500,
        scaleFactor=1.2,        # Better scale invariance
        nlevels=8,              # More pyramid levels for better distribution
        edgeThreshold=31,       # Larger edge threshold to spread features
        firstLevel=0,
        WTA_K=2,
        scoreType=cv2.ORB_HARRIS_SCORE,  # Use Harris corner score for better quality
        patchSize=31,           # Larger patch size
        fastThreshold=20        # Lower threshold to find more features
    )
    
    # Detect keypoints and descriptors
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    
    # Create BFMatcher
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    
    # Match descriptors (get 2 best matches for each descriptor)
    matches = bf.knnMatch(des1, des2, k=2)
    
    # Apply Lowe's ratio test to filter good matches
    good_matches = []
    for match_pair in matches:
        if len(match_pair) == 2:
            m, n = match_pair
            # Keep matches where the distance ratio is less than 0.75
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)
    
    # Sort matches by distance
    good_matches = sorted(good_matches, key=lambda x: x.distance)
    
    # Draw keypoints on individual images
    img1_kp = cv2.drawKeypoints(img1, kp1, None, color=(0,255,0), flags=0)
    img2_kp = cv2.drawKeypoints(img2, kp2, None, color=(0,255,0), flags=0)
    
    # Create combined image with border
    border_width = 20
    h1, w1 = img1.shape
    h2, w2 = img2.shape
    combined_height = max(h1, h2)
    combined_width = w1 + w2 + border_width
    
    # Create white border between images
    combined_img = np.zeros((combined_height, combined_width), dtype=np.uint8)
    combined_img[:h1, :w1] = img1
    combined_img[:, w1:w1+border_width] = 255  # White border
    combined_img[:h2, w1+border_width:] = img2
    
    # Convert to color for drawing matches
    combined_img_color = cv2.cvtColor(combined_img, cv2.COLOR_GRAY2BGR)
    
    # Adjust keypoint coordinates for the second image
    kp2_adjusted = []
    for kp in kp2:
        adjusted_kp = cv2.KeyPoint(kp.pt[0] + w1 + border_width, kp.pt[1], kp.size, kp.angle, kp.response, kp.octave, kp.class_id)
        kp2_adjusted.append(adjusted_kp)
    
    # Draw matches manually on the combined image
    img_matches = combined_img_color.copy()
    for i, match in enumerate(good_matches[:50]):
        # Get keypoint coordinates
        pt1 = tuple(map(int, kp1[match.queryIdx].pt))
        pt2 = tuple(map(int, (kp2[match.trainIdx].pt[0] + w1 + border_width, kp2[match.trainIdx].pt[1])))
        
        # Draw line connecting the matches
        color = tuple(map(int, np.random.randint(0, 255, 3)))  # Random color for each match
        cv2.line(img_matches, pt1, pt2, color, 1)
        cv2.circle(img_matches, pt1, 3, color, -1)
        cv2.circle(img_matches, pt2, 3, color, -1)
    
    # Save images
    base1 = os.path.splitext(os.path.basename(img1_path))[0]
    base2 = os.path.splitext(os.path.basename(img2_path))[0]
    
    cv2.imwrite(f'{base1}_keypoints.jpg', img1_kp)
    cv2.imwrite(f'{base2}_keypoints.jpg', img2_kp)
    cv2.imwrite(f'{base1}_{base2}_matches.jpg', img_matches)
    
    print(f"Found {len(kp1)} keypoints in image 1")
    print(f"Found {len(kp2)} keypoints in image 2")
    print(f"Found {len(good_matches)} good matches out of {len(matches)} total matches")
    print("Saved keypoint and match images")

if __name__ == "__main__":
    main()