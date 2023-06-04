<script lang="ts">
    import VideoOverview from "../../../components/VideoOverview.svelte";
    import type { LayoutServerData } from "./$types";

    export let data: LayoutServerData;
</script>

<h1 class="dash-title">{data.archiveState.name}'s {data.archiveKind}</h1>
<div class="videos">
    {#each data.videos as video}
        <VideoOverview {video} archiveId={data.archiveState.meta.id} />
    {/each}
</div>

<style lang="scss">
    .videos {
        display: grid;
        grid-template-columns: auto auto auto auto;
        margin-right: 20px;
    }
</style>