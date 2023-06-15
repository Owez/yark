<script lang="ts">
    import type { LayoutServerData } from "./$types";

    export let data: LayoutServerData;

    let metaData = data.archiveState.meta.data;
</script>

<h1 class="dash-title">{data.archiveState.name}'s archive</h1>
<div class="cards">
    <a href="/archive/videos" class="card count">
        <p class="number">{metaData.videos_count}</p>
        <p>Videos</p>
    </a>
    <a href="/archive/livestreams" class="card count">
        <p class="number">{metaData.livestreams_count}</p>
        <p>Livestreams</p>
    </a>
    <a href="/archive/shorts" class="card count">
        <p class="number">{metaData.shorts_count}</p>
        <p>Shorts</p>
    </a>
</div>

<style lang="scss">
    $gap: 20px;

    .cards {
        width: 100%;
        display: grid;
        grid-template-columns: auto auto auto;
        gap: $gap;
    }

    .card {
        border-radius: 10px;
        border: 1px solid rgba($color: #000000, $alpha: 0.12);
        min-width: 15rem;
        width: 100%;
        box-shadow: rgba(100, 100, 111, 0.075) 0px 7px 20px 0px;

        &.count {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 7rem;
            text-decoration: none;
            color: inherit;

            p.number {
                font-size: 2.5rem;
                margin-bottom: 0.35rem;
            }
        }
    }
</style>
