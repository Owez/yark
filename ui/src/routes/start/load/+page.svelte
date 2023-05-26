<script lang="ts">
    import type { LayoutServerData } from "../../$types";
    import LoadCard from "../../../components/start/LoadCard.svelte";
    export let data: LayoutServerData;
</script>

<LoadCard recentArchives={data.recentArchives} big={true} back={true} />
