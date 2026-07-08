# 💰 FinWise AI

> An AI-powered Personal Finance Management System built with Flask, Machine Learning, and Interactive Analytics.

---

## 📌 Overview

FinWise AI is a comprehensive personal finance management platform that combines traditional financial tracking with Artificial Intelligence to help users better understand, predict, and improve their financial decisions.

The system allows users to manage transactions, generate reports, receive intelligent recommendations, interact with an AI financial assistant, and predict future financial metrics using trained Machine Learning models.

---

## ✨ Features

### 👤 User Management
- User Registration & Login
- Secure Authentication
- User Profile Management

### 💳 Transactions
- Add Income & Expenses
- Edit & Delete Transactions
- Transaction History
- Financial Categorization

### 📊 Dashboard
- Financial Overview
- Income vs Expense Summary
- Charts & Statistics
- Recent Transactions

### 📈 Reports
- Monthly Reports
- Expense Analysis
- Income Analysis
- Financial Insights

### 🤖 AI Prediction Center

The system includes four Machine Learning models:

#### 1. Salary Prediction
Predicts annual salary based on:

- Age
- Gender
- Education Level
- Job Title
- Years of Experience

Automatically generated features:

- Experience per Age
- Seniority
- Age Group

Output:

- Annual Salary

---

#### 2. Expense Prediction

Predicts monthly expenses using:

- Year
- Month
- Income
- Income Bracket
- Festival
- Festival Count

Output:

- Monthly Expense

---

#### 3. Cost of Living Prediction

Predicts affordability level using:

- Cost of Living Index
- Rent Index
- Cost of Living Plus Rent Index
- Groceries Index
- Restaurant Price Index
- Local Purchasing Power Index
- Income to Cost Ratio

Output:

- Affordability Level

---

#### 4. Inflation Prediction

Predicts future inflation rate using:

- Lag 1
- Lag 2
- Lag 3

Automatically calculated:

- Rolling Mean
- Rolling Standard Deviation

Output:

- Inflation Rate

---

### 💡 Recommendation System

Personalized financial recommendations generated according to the user's financial data stored in the database.

---

### 🤖 AI Financial Assistant

Interactive AI chatbot powered by Hugging Face Inference API.

The assistant can answer financial questions using the user's actual financial data stored in the database.

---

### 📊 Analytics Dashboard (Admin)

Interactive dashboard built using Dash.

Includes:

- Sales Analytics
- Financial KPIs
- Charts
- Trends
- Filters
- Interactive Visualizations

Accessible only by administrators.

---

## 🛠 Tech Stack

### Backend

- Flask
- SQLAlchemy
- SQLite

### Frontend

- HTML
- CSS
- JavaScript

### Machine Learning

- Scikit-learn
- Joblib
- Pandas
- NumPy

### Visualization

- Dash
- Plotly

### AI

- Hugging Face Inference API

---