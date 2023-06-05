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

</style>
