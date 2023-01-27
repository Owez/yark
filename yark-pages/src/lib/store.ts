/**
 * Store/LS utility types and functions
 */

import { writable } from "svelte/store";
import type { Archive } from "./yark";
import { browser } from "$app/environment";

/**
 * Core store interface which automatically saves into `localStorage` if browser is present
 */
export const yarkStore = writable<YarkStore>(yarkStoreInitial())

// Save all changes to the store into window
yarkStore.subscribe((value) => {
    if (browser) {
        window.localStorage.setItem("yarkStore", JSON.stringify(value))
    }
})

/**
 * Gets or creates the initial value of the Yark store depending on if one was already present
 * @returns Relevant initial Yark store
 */
function yarkStoreInitial(): YarkStore {
    const initialValue: YarkStore = { recents: [] }
    if (browser) {
        const foundString = window.localStorage.getItem("yarkStore")
        if (foundString != null) {
            return JSON.parse(foundString)
        }
    }
    return initialValue
}

/**
 * Complete map of the local store state which are expected for all sessions
 */
export interface YarkStore {
    /**
     * Recent archives which where previously opened
     */
    recents: Archive[]
}
