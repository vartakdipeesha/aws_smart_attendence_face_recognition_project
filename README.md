# AWS Smart Attendance System (Face Recognition)

## Overview
This project is a cloud-based automated attendance system built using AWS serverless services. It uses facial recognition to mark attendance in real time and eliminates the need for manual or hardware-based systems.

## Tech Stack
- AWS Rekognition
- AWS Lambda
- Amazon S3
- DynamoDB
- Streamlit

## Features
- Contactless attendance system
- Real-time face recognition
- Automated entry and exit tracking using even-odd logic
- Serverless and scalable architecture
- Secure and tamper-proof data storage

## Workflow
![image](https://github.com/user-attachments/assets/fce2c1e4-8277-4797-9b83-786f8abc93c6)


Example Code Snippet for SmartCampusEntry Lambda: tap_count = student.get('TapCount', 0) + 1
action = 'Entry' if tap_count % 2 == 1 else 'Exit' status = 'Inside' if action == 'Entry' else 'Outside'
 
 ![image](https://github.com/user-attachments/assets/78c8cf10-1ed3-4a9c-a131-052a67b14075)
 ![image](https://github.com/user-attachments/assets/7e6eb073-b9e1-40cc-98a1-583a4708bbff)
 ![image](https://github.com/user-attachments/assets/a84180bd-699d-4601-9db6-b25200b990df)


Face recognition system
1.	If an enrolled student’s face is detected, they are marked Present with confidence shown. Subjects: NH (Nutrition Health)=enrolled

![image](https://github.com/user-attachments/assets/b4543b28-15cf-42ee-b57b-ccb3248640fe)

2.	If a known student (from another class) is detected, it shows Recognized but not enrolled. Subjects: BDA (big dataanalytic)= not enrolled

![image](https://github.com/user-attachments/assets/abea295f-8247-444b-bfed-fc9ea80090d1)

3.	If an unknown face appears, it shows Unknown person detected.
   
![image](https://github.com/user-attachments/assets/5c66c8fc-3c50-4e9b-99e6-117582b2ee65)

4.	If multiple faces appear, the system identifies each one individually and shows results for all (enrolled, not enrolled, orunknown).

![image](https://github.com/user-attachments/assets/d9aefaaa-16f0-40a0-8a57-e2e88c597663)

5.	After stopping the session the absent student status are shown

![image](https://github.com/user-attachments/assets/cdaad6ba-c54f-4424-88bc-ca2a3962d3aa)

6.	Results and Analysis
   
   Recognition Confidence: ≥90%.
   Response Time: 1.5–2 sec.
   Scalability: Auto via PAY_PER_REQUEST. 


## Project Structure
<img width="1293" height="350" alt="Screenshot 2026-03-19 at 1 33 20 AM" src="https://github.com/user-attachments/assets/713f8c2b-e99f-4cb4-b6b8-37d1baf8ebfe" />

## Results
- Recognition Accuracy: 90%+
- Response Time: 1.5–2 seconds
- Fully automated with no manual intervention




## Future Enchancements:

### 1. Location-Based Verification: <br>
Right now, attendance is marked based only on face recognition. This can be misused if someone uploads an image remotely. Adding GPS or IP-based geofencing ensures attendance is only marked when the person is physically present in the campus area.

### 2. Liveness Detection: <br>
The current system can recognize faces but cannot verify if it’s a real person. Liveness detection checks for real-time movements like blinking or slight head motion to prevent misuse using photos or videos, improving system security.

### 3. Real-Time Notifications: <br>
Currently, attendance is stored but users are not notified. Integrating a notification system (like alerts to faculty or students) ensures transparency and helps quickly detect issues like unauthorized access or failed recognition.

### 4. Role-Based Access Control: <br>
At present, the system may have a single dashboard view. By adding role-based access, different users (admin, faculty, student) can have controlled access to only relevant data, improving security and usability.

### 5. Analytics and Reporting: <br>
The system records attendance data, but it is not fully utilized. Adding analytics (like attendance percentage, trends, absentee reports) helps institutions make better decisions and monitor performance effectively.
