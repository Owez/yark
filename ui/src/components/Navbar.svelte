<script lang="ts">
    import { page } from "$app/stores";
    import { getArchiveKind } from "$lib/utils";

    function getButtonPath(path: string | undefined, name: string): string {
        const wantedKind: string | null = getArchiveKind    (path);
        if (wantedKind == name) {
            return `/img/btn${name}_active.svg`;
        }
        return `/img/btn${name}.svg`;
    }
</script>

<nav>
    <div class="sidebar">
        <a href="/archive" class="block logo">Y</a>
        <div class="split" />
        <a href="/archive/videos" class="block">
            <img
                src={getButtonPath($page.url.pathname, "videos")}
                alt="Videos button"
            />
        </a>
        <a href="/archive/livestreams" class="block">
            <img
                src={getButtonPath($page.url.pathname, "livestreams")}
                alt="Livestreams button"
            />
        </a>
        <a href="/archive/shorts" class="block">
            <img
                src={getButtonPath($page.url.pathname, "shorts")}
                alt="Shorts button"
            />
        </a>
    </div>
</nav>

<style lang="scss">
    @use "sass:math";

    $sidebar-width: 50px;
    $gap: 10px;
    $gap-small: 7.5px;
    $gap-large: $gap * 2;
    $radius: 7.5px;
    $radius-small: 5px;
    $border: 1px solid rgba(0, 0, 0, 0.12);

    nav {
        height: 100vh;
        width: calc($sidebar-width + $gap-large);
        flex-shrink: 0;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .sidebar {
        height: calc(100vh - $gap-large);
        width: $sidebar-width;
        border-radius: $radius;
        border: $border;
        display: flex;
        flex-direction: column;
        align-items: center;
        box-sizing: border-box;
        padding-top: $gap-small;
        padding-bottom: $gap-small;
        box-shadow: rgba(100, 100, 111, 0.075) 0px 7px 20px 0px;
    }

    .block {
        $size: calc($sidebar-width - $gap-large);
        width: $size;
        height: $size;
        margin-left: $gap;
        margin-right: $gap;
        margin-top: $gap-small;
        margin-bottom: $gap-small;

        img {
            width: 100%;
            height: 100%;
        }
    }

    .split {
        width: calc($sidebar-width - $gap-large);
        height: 1px;
        background-color: rgba(0, 0, 0, 0.12);
        margin-top: $gap-small;
        margin-bottom: $gap-small;
    }

    .logo {
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 1.45rem;
        text-decoration: none;
        color: initial;
        font-weight: 600;
        margin-bottom: none;
    }
</style>
