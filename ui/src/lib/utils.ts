/**
 * Common utilities for the entire application
 */

import { ArchiveKind } from "./api";

/**
 * Gets a full URL to an image for an archive 
 * @param archiveId The ID of the archive which the image is stored under
 * @param imageHash The ID of the image to retrieve
 * @param base (Optional) The base URL for the API request
 * @returns Full URL string to an image file for use in HTML
 */
export function getImageUrl(archiveId: string, imageHash: string, base?: URL): string {
    const url = base == undefined ? "127.0.0.1:7776" : base.toString()
    return `http://${url}/archive/${archiveId}/image/${imageHash}/file`
}

/**
 * Gets archive kind based on {@link path} provided
 * @param path Ending path of the current url
 */
export function getArchiveKind(
    path: string | undefined
): ArchiveKind | null {
    switch (path) {
        case "/archive/videos":
            return ArchiveKind.Videos;
        case "/archive/livestreams":
            return ArchiveKind.Livestreams;
        case "/archive/shorts":
            return ArchiveKind.Shorts;
        default:
            return null;
    }
}