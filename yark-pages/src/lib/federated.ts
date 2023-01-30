/**
 * Federated server connection discovery system
 */

import { Archive, type ArchivePath } from "./archive";

/**
 * Base URL of a federated server to find an archive on
 */
export type FederatedBaseUrl = string;

/**
 * Single federated server with multiple possible archives attached
 */
export class FederateServer {
    /**
     * Remote URL of this server to connect to
     */
    base: FederatedBaseUrl;
    /**
     * Archive paths that this server advertises
     */
    archives: ArchivePath[];
    // TODO: heartbeat

    constructor(base: FederatedBaseUrl, archives: ArchivePath[]) {
        this.base = base;
        this.archives = archives;
    }

    /**
     * Generates a new set of remote archives to connect to from this server
     * @returns Set of possible archives which can be loaded
     */
    toArchives(): Archive[] {
        return this.archives.map(path => new Archive(path, this.base))
    }
}

export async function findFederated(): Promise<FederateServer[]> {
    fetch("http://127.0.0.1:7666/federated").then(resp => resp.json()).then((data) => {
        console.log(data)
    })
    return [] // TODO
}
