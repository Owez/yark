/**
 * Connector to the official Yark REST API for interfacing
 */

import { goto } from "$app/navigation";
import type { FederatedBaseUrl } from "./federated";
import { yarkStore } from "./store";

/**
 * Type alias for archive paths
 * 
 * - Includes full `/x/y/z` if local
 * - Includes only archive name (or local path) if federated
 */
export type ArchivePath = string;

/**
 * Archive with contains data about a playlist/channel
 */
export class Archive {
    /**
     * Base URL of this archive, if this is null it's a local archive
     */
    base: FederatedBaseUrl | null;
    /**
     * Path to this archive, see {@link ArchivePath}
     */
    path: ArchivePath;
    // TODO: heartbeat

    constructor(path: ArchivePath, base?: FederatedBaseUrl) {
        this.base = base ?? null;
        this.path = path;
    }

    /**
     * Converts a pojo being deserialized into a full archive class
     * @param pojo Pojo version of an archive to convert
     * @returns The archive from it's pojo form
     */
    static fromPojo(pojo: ArchivePojo): Archive {
        return new Archive(pojo.path)
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
    setAsCurrent() {
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
 * Pojo interface for deserializing archives
 */
export interface ArchivePojo { path: string }

/**
 * Loads up an archive and sets it as the currently-active one, then redirects to the dashboard
 * @param path Filepath to load archive from
 */
export function loadArchive(path: string) {
    if (path == undefined) {
        return;
    }
    const archive = new Archive(path);
    archive.setAsCurrent();
    goto('/archive');
}
