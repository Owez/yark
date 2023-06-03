<script lang="ts">
    import type { VideosSnapshot } from "$lib/state";
    import type { LayoutServerData } from "./$types";

    export let data: LayoutServerData;
</script>

<div class="content">
    <h1>Owen's Channel</h1>
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
        <div class="card videos">TODO: videos</div>
        <div class="card videos">TODO: livestreams</div>
        <div class="card videos">TODO: shorts</div>
    </div>
    <div class="card settings"><p>TODO: settings</p></div>
</div>

<style lang="scss">
    $gap: 20px;

    .content {
        margin-left: $gap;
        margin-right: $gap;
    }

    h1 {
        font-size: 2rem;
        font-weight: 500;
        margin-top: 2.25rem;
        margin-bottom: calc($gap * 1.5);
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

        &.videos {
            min-height: 10rem;
            height: 50vh;
        }

        &.settings {
            margin-top: $gap;
        }
    }
</style>
