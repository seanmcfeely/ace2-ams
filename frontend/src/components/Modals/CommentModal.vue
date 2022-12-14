<!-- CommentModal.vue -->
<!-- 'Comment' action modal, agnostic to what is being commented on -->

<template>
  <BaseModal :name="name" header="Add Comment">
    <div>
      <div v-if="error" class="p-col">
        <Message severity="error" @close="handleError">{{ error }}</Message>
      </div>
    </div>
    <div class="p-m-1 p-grid p-fluid p-formgrid p-grid">
      <div class="p-field p-col">
        <Textarea
          v-model="newComment"
          :auto-resize="true"
          rows="5"
          cols="30"
          placeholder="Add a comment..."
        />
      </div>
      <CommentAutocomplete
        @comment-clicked="recentCommentClicked($event)"
      ></CommentAutocomplete>
    </div>
    <template #footer>
      <Button
        label="Nevermind"
        icon="pi pi-times"
        class="p-button-text"
        @click="close"
      />
      <Button
        label="Add"
        icon="pi pi-check"
        :disabled="!allowSubmit"
        @click="addComment"
      />
    </template>
  </BaseModal>
</template>

<script setup lang="ts">
  import { computed, defineEmits, defineProps, ref, inject } from "vue";

  import Button from "primevue/button";
  import Message from "primevue/message";
  import Textarea from "primevue/textarea";

  import BaseModal from "@/components/Modals/BaseModal.vue";
  import CommentAutocomplete from "@/components/Comments/CommentAutocomplete.vue";

  import { AlertComment } from "@/services/api/alertComment";
  import { EventComment } from "@/services/api/eventComment";

  import { useAuthStore } from "@/stores/auth";
  import { objectSelectedStores } from "@/stores/index";
  import { useModalStore } from "@/stores/modal";
  import { useRecentCommentsStore } from "@/stores/recentComments";

  const emit = defineEmits(["requestReload"]);

  const props = defineProps({
    name: { type: String, required: true },
  });

  const objectType = inject("objectType") as "alerts" | "events";
  const authStore = useAuthStore();
  const selectedStore = objectSelectedStores[objectType]();
  const modalStore = useModalStore();
  const recentCommentsStore = useRecentCommentsStore();

  const error = ref<string>();
  const isLoading = ref(false);
  const newComment = ref("");

  async function addComment() {
    isLoading.value = true;
    try {
      if (objectType === "alerts") {
        await AlertComment.create(
          selectedStore.selected.map((uuid) => ({
            username: authStore.user.username,
            submissionUuid: uuid,
            ...commentData.value,
          })),
        );
      } else if (objectType === "events") {
        await EventComment.create(
          selectedStore.selected.map((uuid) => ({
            username: authStore.user.username,
            eventUuid: uuid,
            ...commentData.value,
          })),
        );
      }
    } catch (e: unknown) {
      if (typeof e === "string") {
        error.value = e;
      } else if (e instanceof Error) {
        error.value = e.message;
      }
    }

    isLoading.value = false;
    if (!error.value) {
      recentCommentsStore.addComment(newComment.value);
      close();
      emit("requestReload");
    }
  }

  const commentData = computed(() => {
    return {
      value: newComment.value,
    };
  });

  const allowSubmit = computed(() => {
    return selectedStore.anySelected && newComment.value.length;
  });

  const recentCommentClicked = (comment: string) => {
    newComment.value = comment;
  };

  const handleError = () => {
    error.value = undefined;
    close();
  };

  const close = () => {
    newComment.value = "";
    modalStore.close(props.name);
  };
</script>
