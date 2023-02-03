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
     * Path to this archive, see {@link ArchivePath}
     */
    path: ArchivePath;
    /**
     * Human-readable alias provided for this archive
     */
    alias: string;
    /**
     * Base URL of this archive, if this is null it's a local archive
     */
    base?: FederatedBaseUrl;

    constructor(path: ArchivePath, alias?: string, base?: FederatedBaseUrl) {
        this.path = path;
        this.alias = alias; // TODO: fix the alias
        this.base = base;
    }


    /**
     * Creates a new local archive and returns
     * @param basePath Base path of where to save this local archive to
     * @param name Name of this new local archive
     * @param target Target URL of the playlist/channel
     */
    static createLocal(basePath: string, name: string, target: string): Archive {
        return new Archive("/x/y/z") // TODO
    }

    /**
     * Converts a pojo being deserialized into a full archive class
     * @param pojo Pojo version of an archive to convert
     * @returns The archive from it's pojo form
     */
    static fromPojo(pojo: ArchivePojo): Archive {
        return new Archive(pojo.path, pojo.alias, pojo.base)
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

    async getVideosInfo(): Promise<ArchiveBriefVideo[]> {
        // TODO
    }

    async getLivestreamsInfo(): Promise<ArchiveBriefVideo[]> {
        // TODO
    }

    async getShortsInfo(): Promise<ArchiveBriefVideo[]> {
        // TODO
    }
}

/**
 * Pojo interface for deserializing archives
 */
export interface ArchivePojo { path: string, alias: string, base?: FederatedBaseUrl }

/**
 * Short information on a video, intended to be displayed on a long list
 */
export interface ArchiveBriefVideo {
    /**
     * Video identifier to open to learn more about the video
     */
    id: string,
    /**
     * Current human-readable name of the video
     */
    name: string,
    /**
     * Date it was uploaded to display/sort using
     */
    uploaded: Date,
    /**
     * Current thumbnail identifier of the video to display
     */
    thumbnail: string
}

/**
 * Loads up an archive and sets it as the currently-active one, then redirects to the dashboard
 * @param path Filepath to load archive from
 */
export function loadArchive(path?: string, base?: string) {
    if (path == undefined) {
        return;
    }
    const archive = new Archive(path, base);
    archive.setAsCurrent();
    goto('/archive');
}
