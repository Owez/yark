/**
 * Store/LS utility types and functions
 */

import { writable } from "svelte/store";
import { Archive, type ArchivePojo } from "./yark";
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
    // Create a default value
    const initialValue: YarkStore = { recents: [], openedArchive: null }

    // Try to get local storage if we're in browser
    if (browser) {
        // Get the main storage container
        const foundString = window.localStorage.getItem("yarkStore")

        // Decode if it's present
        if (foundString != null) {
            /**
             * Ad-hoc interface for decoding a Yark store
             */
            interface YarkStorePojo {
                recents: ArchivePojo[],
                openedArchive: ArchivePojo | null
            }

            // Parse the stringified JSON into the Yark store pojo
            const yarkStorePojo: YarkStorePojo = JSON.parse(foundString);

            // Parse into final value and return
            return {
                recents: yarkStorePojo.recents.map(archivePojo => Archive.fromPojo(archivePojo)),
                openedArchive: yarkStorePojo.openedArchive ? Archive.fromPojo(yarkStorePojo.openedArchive) : null
            }
        }
    }

    // Return the default value
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
    /**
     * Currently-opened archive user is using
     */
    openedArchive: Archive | null
}
