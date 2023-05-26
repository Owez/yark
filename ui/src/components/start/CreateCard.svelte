<script lang="ts">
    import StartCard from "./StartCard.svelte";

    export let big = false;
    export let back = false;

    function genHref(): string {
        if (back) {
            return "/start";
        }
        return "/start/create";
    }
</script>

<StartCard
    title="Create new"
    description="Create an archive from scratch to save your channel/playlist"
    {big}
    href={genHref()}
/>
