import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { CardReview } from './components/CardReview';
import { CardGeneration } from './components/CardGeneration';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/review" replace />} />
        <Route path="/review" element={<CardReview />} />
        <Route path="/generate" element={<CardGeneration />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
