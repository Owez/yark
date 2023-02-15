/**
 * Store/LS utility types and functions
 */

import { writable } from 'svelte/store';
import type { Archive } from './archive';
import { invoke } from '@tauri-apps/api';
import { browser } from '$app/environment';

/**
 * Main store interface which automatically saves into `localStorage` if browser is present
 */
export const yarkStore = writable(yarkStoreInitial());

// Save all changes to the main Yark store into the `localStorage` in the window
yarkStore.subscribe((value) => {
	if (!browser) return;

	window.localStorage.setItem('yarkStore', JSON.stringify(value));
});

/**
 * Gets or creates the initial value of the Yark store depending on if one was already present
 * @returns Relevant initial Yark store
 */
function yarkStoreInitial(): YarkStore {
	// workaround for sveltekit ssr for some reason running during development
	if (!browser) return createEmptyYarkStore();

	// Get the main storage container
	const foundString = window.localStorage.getItem('yarkStore');

	// Decode and return if it's present
	if (foundString != null) {
		return JSON.parse(foundString);
	}

	// Return the default value if we couldn't get and decode an existing one
	return createEmptyYarkStore();
}

/**
 * Creates an empty store for use when we don't know what the store is, or when we need phantom data
 * @returns Empty version of a store
 */
function createEmptyYarkStore(): YarkStore {
	return { recents: [], openedArchive: undefined, federatedAccept: false };
}

/**
 * Main store containing everything that should be stored in `localStorage`
 */
export interface YarkStore {
	/**
	 * Recent archives which where previously opened
	 */
	recents: Archive[];
	/**
	 * Currently-opened archive user is using
	 */
	openedArchive?: Archive;
	/**
	 * If the user accepted to view the potentially bad content on the federated listings
	 */
	federatedAccept: boolean;
}

/**
 * Gets the local secret token for use inside of the API from the environment
 * @returns Local secret token
 */
export function getLocalSecret(): Promise<string> {
	return invoke('get_environment_variable', { name: 'YARK_LOCAL_SECRET' });
}
