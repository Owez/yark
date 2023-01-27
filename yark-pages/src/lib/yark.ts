/** Connector to the official Yark REST API for interfacing */

import { goto } from "$app/navigation";
import { yarkStore } from "./store";

/**
 * Archive with contains data about a playlist/channel
 */
export class Archive {
    path: string;

    constructor(path: string) {
        this.path = path;
    }

    /**
     * Parses the path value into a readable archive name
     * @returns Name from path
     */
    getName(): string {
        const splitted = this.path.split("/")
        return splitted[splitted.length - 1]
    }

    /**
     * Set this archive as the currently-opened one, also adds to recent archives
     */
    setCurrent() {
        yarkStore.update(value => {
            // Set opened archive to this
            value.openedArchive = this

            // Add to recent list
            if (value.recents.length >= 10) {
                value.recents.shift()
            }
            value.recents.push(this)

            // Return updated value
            return value
        })
    }
}

/**
 * Loads up an archive and sets it as the currently-active one, then redirects to the dashboard
 * @param filepath Filepath to load archive from
 */
export function loadArchive(filepath: string) {
    if (filepath == undefined) {
        return;
    }
    const archive = new Archive(filepath);
    archive.setCurrent();
    goto('/archive');
}
