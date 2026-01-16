import { useState, useEffect, useCallback } from 'react';
import type { CardWithValidation, Card, AnkiStatus } from '../types';
import { loadCards, updateCard, pingAnki, addCardToAnki } from '../api/client';

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

        setState((prev) => ({
          ...prev,
          filename: currentFilename,
          cards: cardsResponse.cards,
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
    if (!currentCard) return;

    setState((prev) => ({ ...prev, isSubmitting: true }));

    try {
      const response = await addCardToAnki(currentCard.card);

      if (response.success) {
        setState((prev) => ({
          ...prev,
          addedCount: prev.addedCount + 1,
          isSubmitting: false,
        }));
        goToNext();
      } else {
        setState((prev) => ({
          ...prev,
          isSubmitting: false,
          error: response.error || 'Failed to add card',
        }));
      }
    } catch (err) {
      setState((prev) => ({
        ...prev,
        isSubmitting: false,
        error: err instanceof Error ? err.message : 'Failed to add card',
      }));
    }
  }, [currentCard, goToNext]);

  const skip = useCallback(() => {
    setState((prev) => ({
      ...prev,
      skippedCount: prev.skippedCount + 1,
    }));
    goToNext();
  }, [goToNext]);

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
