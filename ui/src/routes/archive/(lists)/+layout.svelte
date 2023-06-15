<script lang="ts">
    import VideoOverview from "../../../components/VideoOverview.svelte";
    import type { LayoutServerData } from "./$types";

    export let data: LayoutServerData;

    let metaData = data.archiveState.meta.data;
</script>

<h1 class="dash-title">{data.archiveState.name}'s {data.archiveKind}</h1>
<div class="videos">
    {#each data.videos as video}
        <VideoOverview {video} archiveId={metaData.id} />
    {/each}
</div>

<!-- NOTE: actual pages are empty but i like the routing and futureproofing -->
<slot />

<style lang="scss">
    .videos {
        display: grid;
        grid-template-columns: auto auto auto auto;
        margin-right: 20px;
    }
</style>
