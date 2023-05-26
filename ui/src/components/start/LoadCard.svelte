<script lang="ts">
    import type { RecentArchive } from "$lib/state";
    import LoadItem from "./LoadItem.svelte";
    import StartCard from "./StartCard.svelte";

    export let recentArchives: RecentArchive[];
    export let big = false;
    export let back = false;

    function genHref(): string {
        if (back) {
            return "/start";
        }
        return "/start/load";
    }
</script>

<StartCard
    title="Load existing"
    description="Manage/view an existing archive that you've already created"
    ball={1}
    {big}
    href={genHref()}
>
    {#each recentArchives as recentArchive}
        <LoadItem {recentArchive} />
    {/each}
</StartCard>
