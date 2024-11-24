# Top Five Backend

## Overview

Top Five is an innovative dating application designed to create meaningful connections through a unique matching algorithm. This repository contains the Django-based REST API backend that powers both the iOS and Android mobile applications.

The application focuses on quality over quantity in matches, employing sophisticated filtering and a novel approach to user interactions. It emphasizes secure data handling and scalable architecture to support a growing user base.

## Technology Stack

- **Framework**: Django 5.0.7 with Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens) with Simple JWT
- **Cloud Services**: AWS S3 for media storage
- **Language**: Python 3.11
- **API Design**: RESTful architecture

## Key Features

- **Advanced Authentication System**
  - JWT-based authentication with refresh token mechanism
  - Secure password handling
  - Session management

- **Comprehensive Profile Management**
  - Detailed user profiles with extensive customization
  - Multi-photo support with S3 integration
  - Profile verification system

- **Matching System**
  - Sophisticated matching algorithm
  - Preference-based filtering
  - Profile ranking system

- **Security-First Design**
  - Encrypted data storage
  - Secure media handling
  - Privacy protection measures

## API Endpoints

### Authentication
- `POST /api/users/login/` - User authentication
- `POST /api/users/logout/` - Session termination
- `POST /api/token/refresh/` - JWT refresh

### Profile Management
- `GET /api/users/get_profile/<id>/` - Profile retrieval
- `PUT /api/users/update_profile/<id>/` - Profile updates
- `PUT /api/users/get_presigned_urls/<id>/` - Photo upload management

### User Interactions
- `GET /api/users/potential_matches/` - Match suggestions
- `GET /api/users/matches/` - Current matches

### Account Management
- `POST /api/users/signup/` - Account creation
- `PUT /api/users/update_user/<id>/` - Account updates
- `POST /api/users/change_password/` - Password management

## Security Features

- **Authentication**
  - JWT token-based system
  - Token blacklisting
  - Refresh token rotation

- **Data Protection**
  - Encrypted data storage
  - Secure password hashing
  - Protected API endpoints

- **Media Security**
  - S3 presigned URLs
  - Temporary access tokens
  - Secure file uploads

- **Infrastructure**
  - CORS protection
  - Rate limiting
  - Input validation

## Intellectual Property Notice

© 2024 All Rights Reserved

This is a proprietary application intended for commercial release on the Apple App Store and Google Play Store. This codebase represents confidential intellectual property with all rights reserved. The implementation, design patterns, and algorithms contained within are protected by copyright law and are the exclusive property of the owner.

**Usage Restrictions:**
- This code is private and proprietary
- No part may be reproduced or distributed
- All rights reserved for commercial use
- Future app store deployment protected

The unique matching algorithm, user interaction patterns, and overall application concept are proprietary innovations intended for commercial deployment.

## For Recruiters and Hiring Managers

This project demonstrates:

**Technical Proficiency**
- Modern Django/Python development
- RESTful API design and implementation
- Cloud service integration (AWS)
- Authentication system design
- Database modeling and optimization

**Architecture Highlights**
- Scalable backend design
- Security-first implementation
- Clean code practices
- Comprehensive API documentation
- Mobile-first architecture

**Project Management**
- End-to-end feature implementation
- Commercial-grade security measures
- App store deployment preparation
- User privacy protection

This project represents both technical expertise and commercial development capabilities, showcasing the ability to build production-ready applications with market potential.

## Contact

For professional inquiries or detailed technical discussions, please reach out through [LinkedIn](https://www.linkedin.com/in/rashaun-warner/) or email me at RashaunWarner.com.