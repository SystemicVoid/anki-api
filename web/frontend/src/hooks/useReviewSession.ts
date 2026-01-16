import { useState, useEffect, useCallback } from 'react';
import type { CardWithValidation, Card, AnkiStatus } from '../types';
import { loadCards, updateCard, pingAnki, approveCard, skipCard } from '../api/client';

export interface ReviewSessionState {
  filename: string;
  cards: CardWithValidation[];
  currentIndex: number;
  addedCount: number;
  skippedCount: number;
  isComplete: boolean;
  isEditing: boolean;
  isLoading: boolean;
  isSubmitting: boolean;
  error: string | null;
  ankiStatus: AnkiStatus;
}

export function useReviewSession(filename: string | null) {
  const [state, setState] = useState<ReviewSessionState>({
    filename: filename || '',
    cards: [],
    currentIndex: 0,
    addedCount: 0,
    skippedCount: 0,
    isComplete: false,
    isEditing: false,
    isLoading: true,
    isSubmitting: false,
    error: null,
    ankiStatus: { connected: false },
  });

  // Load cards and check Anki status
  useEffect(() => {
    if (!filename) {
      setState((prev) => ({ ...prev, isLoading: false }));
      return;
    }

    const currentFilename = filename;

    async function initialize() {
      try {
        const [cardsResponse, ankiResponse] = await Promise.all([
          loadCards(currentFilename),
          pingAnki(),
        ]);

        // Calculate initial counts based on status
        const initialAdded = cardsResponse.cards.filter(c => c.card.status === 'added').length;
        const initialSkipped = cardsResponse.cards.filter(c => c.card.status === 'skipped').length;

        setState((prev) => ({
          ...prev,
          filename: currentFilename,
          cards: cardsResponse.cards,
          addedCount: initialAdded,
          skippedCount: initialSkipped,
          isLoading: false,
          error: null,
          ankiStatus: ankiResponse,
        }));
      } catch (err) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: err instanceof Error ? err.message : 'Failed to load cards',
        }));
      }
    }

    initialize();
  }, [filename]);

  const currentCard = state.cards[state.currentIndex] ?? null;

  const goToNext = useCallback(() => {
    setState((prev) => {
      const nextIndex = prev.currentIndex + 1;
      if (nextIndex >= prev.cards.length) {
        return { ...prev, isComplete: true, isEditing: false };
      }
      return { ...prev, currentIndex: nextIndex, isEditing: false };
    });
  }, []);

  const approve = useCallback(async () => {
    if (!currentCard || !filename) return;

    setState((prev) => ({ ...prev, isSubmitting: true }));

    try {
      // Use the new approveCard endpoint which persists ID to file
      const updatedCard = await approveCard(filename, state.currentIndex);

      setState((prev) => {
        const newCards = [...prev.cards];
        newCards[prev.currentIndex] = updatedCard; // Update card with anki_id and status

        // Only increment if the card wasn't already added
        const increment = prev.cards[prev.currentIndex].card.status !== 'added' ? 1 : 0;

        return {
          ...prev,
          cards: newCards,
          addedCount: prev.addedCount + increment,
          isSubmitting: false,
        };
      });
      goToNext();
    } catch (err) {
      setState((prev) => ({
        ...prev,
        isSubmitting: false,
        error: err instanceof Error ? err.message : 'Failed to approve card',
      }));
    }
  }, [currentCard, filename, state.currentIndex, goToNext]);

  const skip = useCallback(async () => {
    if (!currentCard || !filename) return;

    setState((prev) => ({ ...prev, isSubmitting: true }));

    try {
      // Persist skip to backend
      const updatedCard = await skipCard(filename, state.currentIndex);

      setState((prev) => {
        const newCards = [...prev.cards];
        newCards[prev.currentIndex] = updatedCard; // Update card with status='skipped'

        // Only increment if the card wasn't already skipped
        const increment = prev.cards[prev.currentIndex].card.status === 'pending' ? 1 : 0;

        return {
          ...prev,
          cards: newCards,
          skippedCount: prev.skippedCount + increment,
          isSubmitting: false,
        };
      });
      goToNext();
    } catch (err) {
      setState((prev) => ({
        ...prev,
        isSubmitting: false,
        error: err instanceof Error ? err.message : 'Failed to skip card',
      }));
    }
  }, [currentCard, filename, state.currentIndex, goToNext]);

  const quit = useCallback(() => {
    setState((prev) => ({ ...prev, isComplete: true }));
  }, []);

  const startEditing = useCallback(() => {
    setState((prev) => ({ ...prev, isEditing: true }));
  }, []);

  const cancelEditing = useCallback(() => {
    setState((prev) => ({ ...prev, isEditing: false }));
  }, []);

  const saveEdit = useCallback(
    async (updates: Partial<Pick<Card, 'front' | 'back' | 'context' | 'tags'>>) => {
      if (!filename || !currentCard) return;

      setState((prev) => ({ ...prev, isSubmitting: true }));

      try {
        const updatedCard = await updateCard(filename, state.currentIndex, updates);

        setState((prev) => {
          const newCards = [...prev.cards];
          newCards[prev.currentIndex] = updatedCard;
          return {
            ...prev,
            cards: newCards,
            isEditing: false,
            isSubmitting: false,
          };
        });
      } catch (err) {
        setState((prev) => ({
          ...prev,
          isSubmitting: false,
          error: err instanceof Error ? err.message : 'Failed to save changes',
        }));
      }
    },
    [filename, currentCard, state.currentIndex]
  );

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  const refreshAnkiStatus = useCallback(async () => {
    try {
      const status = await pingAnki();
      setState((prev) => ({ ...prev, ankiStatus: status }));
    } catch {
      setState((prev) => ({ ...prev, ankiStatus: { connected: false } }));
    }
  }, []);

  return {
    ...state,
    currentCard,
    approve,
    skip,
    quit,
    startEditing,
    cancelEditing,
    saveEdit,
    clearError,
    refreshAnkiStatus,
  };
}
