<script lang="ts">
    import { getCurrentElementDefo, type Video } from "$lib/archive";
    import { getImageUrl } from "$lib/utils";

    export let archiveId: string;
    export let video: Video;

    $: currentThumbnailUrl = getImageUrl(
        archiveId,
        getCurrentElementDefo(video.thumbnail).data
    );
    $: currentTitle = getCurrentElementDefo(video.title).data;
</script>

<div class="video">
    <img src={currentThumbnailUrl} alt={currentTitle} />
    <!-- TODO: info -->
</div>

<style lang="scss">
    .video {
        aspect-ratio: 16/10;
        margin: 20px;
        margin-left: 0;
        margin-top: 0;
        display: flex;
        flex-direction: column;
    }
</style>
