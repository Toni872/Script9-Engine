import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';
import { getAnalytics } from 'firebase/analytics';

const firebaseConfig = {
  apiKey: 'AIzaSyA-0EApyHFDxK2541RQwmcfNlipusd2uqQ',
  authDomain: 'script9-engine.firebaseapp.com',
  projectId: 'script9-engine',
  storageBucket: 'script9-engine.firebasestorage.app',
  messagingSenderId: '694894317828',
  appId: '1:694894317828:web:9e96ec31bc2fe456020051',
  measurementId: 'G-EXSMXJQKHM',
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();

// Analytics solo en producción
if (import.meta.env.PROD) {
  getAnalytics(app);
}
