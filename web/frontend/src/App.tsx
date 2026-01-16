import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { CardReview } from './components/CardReview';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/review" replace />} />
        <Route path="/review" element={<CardReview />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
