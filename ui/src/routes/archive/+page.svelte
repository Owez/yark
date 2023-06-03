<script lang="ts">
    import type { LayoutServerData } from "./$types";

    export let data: LayoutServerData;
</script>

<div class="content">
    <h1 class="dash-title">Owen's Channel</h1>
    <div class="cards">
        <a href="/archive/videos" class="card count">
            <p class="number">{data.archiveState.meta.videos_count}</p>
            <p>Videos</p>
        </a>
        <a href="/archive/livestreams" class="card count">
            <p class="number">{data.archiveState.meta.livestreams_count}</p>
            <p>Livestreams</p>
        </a>
        <a href="/archive/shorts" class="card count">
            <p class="number">{data.archiveState.meta.shorts_count}</p>
            <p>Shorts</p>
        </a>
    </div>
</div>

<style lang="scss">
    $gap: 20px;

    .content {
        margin-left: $gap;
        margin-right: $gap;
    }

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
