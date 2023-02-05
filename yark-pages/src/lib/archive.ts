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
    server: string;
    slug: string;

    constructor(server: string, slug: string) { this.server = server; this.slug = slug; }

    /**
     * Creates and saves a brand new archive
     * @param server Server URL to connect to
     * @param slug Unique slug for the new archive
     * @param path Path to save the new archive to (including final directory name)
     * @param target The URL to target, e.g., playlist or channel
     * @returns Newly-created archive
     */
    static async createNew(server: string, slug: string, path: string, target: string): Promise<Archive> {
        const payload = { slug: slug, path: path, target: target };
        return await fetch(server + "/archive?intent=create", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }).then(resp => resp.json()).then(resp_json => {
            const slug = resp_json.slug;
            return new Archive(server, slug)
        })
    }

    /**
     * Imports an existing archive already saved to a file location
     * @param server Server URL to connect to
     * @param slug Unique slug for the new archive
     * @param path Path to save the new archive to (including final directory name)
     * @returns Newly-imported archive
     */
    static async createExisting(server: string, slug: string, path: string): Promise<Archive> {
        const payload = { slug: slug, path: path };
        return await fetch(server + "/archive?intent=existing", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }).then(resp => resp.json()).then(resp_json => {
            const slug = resp_json.slug;
            return new Archive(server, slug)
        })
    }

    /**
     * Converts a pojo being deserialized into a full archive class
     * @param pojo Pojo version of an archive to convert
     * @returns The archive from it's pojo form
     */
    static fromPojo(pojo: ArchivePojo): Archive {
        return new Archive(pojo.server, pojo.slug)
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
        goto(`/archive/${this.slug}/videos`)
    }
}

/**
 * Pojo interface for deserializing archives
 */
export interface ArchivePojo { server: string; slug: string; }

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
