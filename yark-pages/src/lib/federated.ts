/**
 * Federated server connection discovery system
 */

import type { ArchivePath } from "./archive";


/**
 * Base URL of a federated server to find an archive on
 */
export type FederatedBaseUrl = string;

/**
 * Single federated server with multiple possible archives attached
 */
export class FederateServer {
    /**
     * Cosmetic name of this server to display
     */
    name: string;
    /**
     * Remote URL of this server to connect to
     */
    base: FederatedBaseUrl;
    /**
     * Archive paths that this server advertises
     */
    archives: ArchivePath[];
    /**
     * Last known activity from this server
     */
    heartbeat: Date;

    constructor(name: string, base: FederatedBaseUrl, archives: ArchivePath[], heartbeat: Date | string) {
        this.name = name;
        this.base = base;
        this.archives = archives;
        if (typeof heartbeat == "string") {
            this.heartbeat = new Date(heartbeat);
        } else {
            this.heartbeat = heartbeat;
        }
    }
}

/**
 * Finds federated servers by contacting the remote discovery system
 * @returns Federated servers which have been discovered
 */
export async function findFederated(): Promise<FederateServer[]> {
    fetch("http://127.0.0.1:7666/federated").then(resp => resp.json()).then((data) => {
        console.log(data)
    })
    return [] // TODO
}
