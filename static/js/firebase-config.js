// Firebase 설정
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-analytics.js";

const firebaseConfig = {
  apiKey: "AIzaSyCaA9vqwRBpax3cdU5x4TfEw2hA13KdHx0",
  authDomain: "insta-analysis-55592.firebaseapp.com",
  projectId: "insta-analysis-55592",
  storageBucket: "insta-analysis-55592.firebasestorage.app",
  messagingSenderId: "288337565994",
  appId: "1:288337565994:web:889c34215c7e40311e6653",
  measurementId: "G-V5RXZK23B4"
};

// Firebase 초기화
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// API URL 설정
export const API_URL = 'https://insta-analysis.vercel.app/api'; // Vercel 배포 URL