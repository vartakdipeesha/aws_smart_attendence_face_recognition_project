# AWS Smart Attendance System (Face Recognition)

## Overview
This project is a cloud-based automated attendance system built using AWS serverless services. It uses facial recognition to mark attendance in real time and eliminates the need for manual or hardware-based systems.

## Tech Stack
- AWS Rekognition
- AWS Lambda
- Amazon S3
- DynamoDB
- Streamlit

## Architecture
![image](https://github.com/user-attachments/assets/6f0ed2eb-90fa-49b7-8bff-ee7eccb04214)


## Features
- Contactless attendance system
- Real-time face recognition
- Automated entry and exit tracking using even-odd logic
- Serverless and scalable architecture
- Secure and tamper-proof data storage

## Workflow
1. Enrollment: Student images uploaded to S3
2. Verification: Rekognition matches faces
3. Attendance Marking: Lambda updates DynamoDB
4. Entry/Exit Logic: Even-odd tracking mechanism
5. Dashboard: Live attendance monitoring via Streamlit

## Results
- Recognition Accuracy: 90%+
- Response Time: 1.5–2 seconds
- Fully automated with no manual intervention

## Project Structure
<img width="1293" height="350" alt="Screenshot 2026-03-19 at 1 33 20 AM" src="https://github.com/user-attachments/assets/713f8c2b-e99f-4cb4-b6b8-37d1baf8ebfe" />

