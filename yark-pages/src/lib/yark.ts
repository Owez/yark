/** Connector to the official Yark REST API for interfacing */

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
     * Gets the pages archive path
     * @returns Relative URL to archive
     */
    getUrl(): string {
        return `/archive/?path=${encodeURIComponent(this.path)}`
    }

    /**
     * Adds current archive to the recent list
     */
    setRecent() {
        yarkStore.update(value => {
            if (value.recents.length >= 10) {
                value.recents.shift()
            }
            value.recents.push(this)
            return value
        })
    }
}
