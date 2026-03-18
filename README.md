# SMART CAMPUS ATTENDANCE SYSTEM USING AWS FACIAL RECOGNITION 

## Overview
This project is a cloud-based automated attendance system built using AWS serverless services. It uses facial recognition to mark attendance in real time and eliminates the need for manual or hardware-based systems.

## Tech Stack
- AWS Rekognition
- AWS Lambda
- Amazon S3
- DynamoDB
- Streamlit


## Workflow
![image](https://github.com/user-attachments/assets/fce2c1e4-8277-4797-9b83-786f8abc93c6)

1.Uploading the images and Creating the Database Environment​

2.Set up S3 event notification (Console)​

3.Creating DB table for timetable​

4.Enroll Students in Rekognition Collection​

5.Enroll-Indexer Lambda​

6.Entry and Exit​

7.Dashborad creation  


## Uploading the images and Creating the Database Environment

Step 1: Verify the collection was created
<img width="941" height="243" alt="image" src="https://github.com/user-attachments/assets/b3d6d895-506e-4f26-a1c6-f7ff63433465" />


Step 2: Create the enroll/ folder in S3

awss3api put-object --bucket smart-campus-students --key enroll/

Step 3: Index your 4 students with SAP IDs

awsrekognitionindex-faces --collection-id attendance-prod --image "S3Object={Bucket=smart-campus-students,Name=Dhruvi.png}" --external-image-id "70322000160" --region ap-south-1
12

<img width="847" height="368" alt="image" src="https://github.com/user-attachments/assets/fa1c3a2a-a1c2-402c-b44b-aa9388e46e44" />


## Set up S3 event notification (Console)

1. Go to S3 Console→ smart-campus-studentsbucket
2. Click Propertiestab
3. Scroll down to Event notifications
4. Click Create event notification
5. Fill in:
·Event name: enroll-events
·Prefix: enroll/
·Event types: Check All object create events
·Destination: SQS queue -> Select enroll-queue
6. Click Save changes


   <img width="1378" height="470" alt="image" src="https://github.com/user-attachments/assets/ba18176c-3497-42f9-b16d-d6d4bff16c5f" />

## Creating DB table for timetable



<img width="949" height="570" alt="image" src="https://github.com/user-attachments/assets/c8792a76-432d-4040-bac6-37a8fbdb4a30" />
<img width="987" height="512" alt="image" src="https://github.com/user-attachments/assets/c39dd9ee-de25-449a-95d4-3a092e8e41a2" />
<img width="1600" height="1460" alt="image" src="https://github.com/user-attachments/assets/5d652c82-c597-4457-ab2b-5c9b418f488d" />



## EnrollStudents in RekognitionCollection

Create Rekognitioncollection
awsrekognitioncreate-collection --collection-id AttendanceCollection



<img width="952" height="349" alt="image" src="https://github.com/user-attachments/assets/54f684d7-2527-4c4c-ae18-a56b96153e17" />
<img width="1024" height="522" alt="image" src="https://github.com/user-attachments/assets/b99c5ec8-b9b4-487a-bf8f-1fe4fbee8bb9" />


## Enroll-Indexer Lambda

1. Created Lambda function

Function name:SmartCampusEntry

Runtime:Python 3.13

Purpose:Record student attendance in DynamoDB tables (studentsand DailyPresent).

Code:HandlesSAP_ID input, determines Entry/Exit, updates student status, and logs in DailyPresent.

2. Created DynamoDB Tables

students table:stores student info including TapCountand Status.

DailyPresenttable:stores daily attendance logs with fields:

SAP_ID
Date
LastAction
LastTimestamp

3. Created IAM Policy
Policy name:DailyPresentAccess
Type:Customer managed
Purpose:Allow Lambda function to GetItem, PutItem, and UpdateItemon DailyPresent.

4.Attached IAM Policy

Initially had issues attaching DailyPresentAccessto your Lambda execution role.
Now it is attached to attendance-lambda-role, giving Lambda proper permissions.

5.Tested Lambda

You ran a test event (Testtab1.1) with a sample SAP_ID.
DynamoDB updated successfully:
Last tap was recorded as Exit.
Table shows correct LastActionand LastTimestamp.

<img width="931" height="489" alt="image" src="https://github.com/user-attachments/assets/185cc0ff-4c67-4497-8b3b-4aa95dd06b29" />
<img width="870" height="487" alt="image" src="https://github.com/user-attachments/assets/d0d959e2-04fb-4bc3-9172-1b266795e4b2" />

## Entry and Exit
<img width="1598" height="301" alt="image" src="https://github.com/user-attachments/assets/63e9b2cb-fd9d-4ca8-9338-a6d4044fbc18" />
<img width="1600" height="1234" alt="image" src="https://github.com/user-attachments/assets/27bad78f-b522-4c8a-9c42-2bb84f02969a" />
<img width="966" height="668" alt="image" src="https://github.com/user-attachments/assets/41689fa2-71b2-44ad-9de6-f3ebf8c93a72" />

## Login dashboard creation

<img width="966" height="668" alt="image" src="https://github.com/user-attachments/assets/7e9c3f23-3bfe-4d03-949c-f4efd4be735c" />

## Faculty dashboard creation: handles all four cases

1) Case1: If an enrolled student’s face is detected, they are markedPresentwith confidence shown. Subjects: NH (Nutrition Health) =enrolled
   
   <img width="940" height="554" alt="image" src="https://github.com/user-attachments/assets/589749b9-4377-4091-815c-01ac7415cf49" />

2) Case2: If a known student (from another class) is detected, it shows Recognized but not enrolled. Subjects: BDA (big data analytic)= not enrolled

   <img width="940" height="568" alt="image" src="https://github.com/user-attachments/assets/0228ca65-53e1-43a2-98de-b6a3c32e36b5" />

3) Case3: If an unknown face appears, it shows Unknown person detected

<img width="940" height="540" alt="image" src="https://github.com/user-attachments/assets/0bad2d52-ffdb-4439-b1d0-d6da041b0a75" />

4) Case4: If multiple faces appear, the system identifies each one individually and shows results for all (enrolled, not enrolled, or unknown).

<img width="940" height="537" alt="image" src="https://github.com/user-attachments/assets/30c38568-f19a-440f-879d-9db621914753" />

5)After stoping the session the absent student status are shown

<img width="1406" height="799" alt="image" src="https://github.com/user-attachments/assets/e9d6294f-005d-4e51-9e66-b4bdeb028a9c" />

## Student dashboard creation



<img width="1683" height="862" alt="image" src="https://github.com/user-attachments/assets/2cacd60f-7917-47f3-8575-8614517dcb64" />
<img width="2418" height="1068" alt="image" src="https://github.com/user-attachments/assets/17a63f66-8b15-4df6-a512-8b3a20d8b8ba" />

<img width="2392" height="1288" alt="image" src="https://github.com/user-attachments/assets/5db7d153-ef83-47b5-9602-a8e37b6280f8" />

## Conclusion

The AWS-based Face Recognition and Location Tracking system automates attendance and enables real-time student monitoring with high accuracy and scalability.

Using Amazon Rekognitionit ensures precise identification and secure data handling through DynamoDB, S3,AWS lambda,APIGateway and IAM controls.

This cloud-native, serverless design reduces manual effort, minimizes errors, and supports centralized monitoring via an admin dashboard.

Its flexible architecture is ready for campus-wide deployment and future expansion

















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
