/**
 * Store/LS utility types and functions
 */

import { writable } from "svelte/store";
import { Archive, type ArchivePojo } from "./archive";
import { invoke } from "@tauri-apps/api";

/**
 * Main store interface which automatically saves into `localStorage` if browser is present
 */
export const yarkStore = writable(yarkStoreInitial())
// TODO: figure out why sveltekit is fucking up here, doesnt seem like `window` is my fault if ive turned ssr completely off then its still ssr'ing??
//       maybe its tauri? not sure. don't think so

// Save all changes to the main Yark store into the `localStorage` in the window
yarkStore.subscribe((value) => {
    window.localStorage.setItem("yarkStore", JSON.stringify(value))
})

/**
 * Gets or creates the initial value of the Yark store depending on if one was already present
 * @returns Relevant initial Yark store
 */
function yarkStoreInitial(): YarkStore {
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
            federatedAccept: boolean
        }

        // Parse the stringified JSON into the Yark store pojo
        const yarkStorePojo: YarkStorePojo = JSON.parse(foundString);

        // Parse into final value and return
        return {
            recents: yarkStorePojo.recents.map(archivePojo => Archive.fromPojo(archivePojo)),
            openedArchive: yarkStorePojo.openedArchive ? Archive.fromPojo(yarkStorePojo.openedArchive) : null,
            federatedAccept: yarkStorePojo.federatedAccept
        }
    }

    // Return the default value if we couldn't get and decode an existing one
    return { recents: [], openedArchive: null, federatedAccept: false }
}

/**
 * Main store containing everything that should be stored in `localStorage`
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
    /**
     * If the user accepted to view the potentially bad content on the federated listings
     */
    federatedAccept: boolean
}

/**
 * Gets the local secret token for use inside of the API from the environment
 * @returns Local secret token
 */
export function getLocalSecret(): Promise<string> {
    return invoke("get_environment_variable", { name: "YARK_LOCAL_SECRET" })
}
