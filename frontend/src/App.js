import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import NewConclusion from './pages/NewConclusion';
import ConclusionEditor from './pages/ConclusionEditor';
import FAQPage from './pages/FAQPage';
import CGUPage from './pages/CGUPage';
import PricingPage from './pages/PricingPage';
import PaymentSuccess from './pages/PaymentSuccess';
import ProtectedRoute from './components/ProtectedRoute';
import { Toaster } from './components/ui/sonner';

function AppRouter() {  
  return (
    <>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/faq" element={<FAQPage />} />
        <Route path="/cgu" element={<CGUPage />} />
        <Route path="/tarifs" element={<PricingPage />} />
        <Route path="/payment-success" element={
          <ProtectedRoute>
            <PaymentSuccess />
          </ProtectedRoute>
        } />
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        <Route path="/new-conclusion" element={
          <ProtectedRoute>
            <NewConclusion />
          </ProtectedRoute>
        } />
        <Route path="/conclusion/:conclusionId" element={
          <ProtectedRoute>
            <ConclusionEditor />
          </ProtectedRoute>
        } />
      </Routes>
      <Toaster />
    </>
  );
}

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
    </div>
  );
}

export default App;