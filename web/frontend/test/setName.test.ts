import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { parseSetName } from '../src/utils/setName.ts';

describe('parseSetName', () => {
  it('preserves a full generator timestamp as visible revision metadata', () => {
    const firstRevision = parseSetName('linear_transformations_matrices_20260117_192547.json');
    const secondRevision = parseSetName('linear_transformations_matrices_20260117_192558.json');

    assert.deepEqual(firstRevision, {
      title: 'linear transformations matrices',
      source: null,
      revision: {
        label: '20260117 · 192547',
        dateTime: '2026-01-17T19:25:47',
      },
    });
    assert.equal(secondRevision.title, firstRevision.title);
    assert.deepEqual(secondRevision.revision, {
      label: '20260117 · 192558',
      dateTime: '2026-01-17T19:25:58',
    });
  });

  it('preserves a date-only generator timestamp', () => {
    assert.deepEqual(parseSetName('codesignal-array-search_20260117.json'), {
      title: 'array search',
      source: 'codesignal',
      revision: {
        label: '20260117',
        dateTime: '2026-01-17',
      },
    });
  });

  it('does not treat ordinary trailing digits as a revision', () => {
    assert.deepEqual(parseSetName('chapter_2026.json'), {
      title: 'chapter 2026',
      source: null,
      revision: null,
    });
  });
});
