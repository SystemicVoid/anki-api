import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { CardGeneration } from './components/CardGeneration';
import { CardReview } from './components/CardReview';

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
