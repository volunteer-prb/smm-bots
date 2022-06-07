export interface TG_Update {
  message?: {
    chat: {
      id: string;
    },
    text: string;
    from: {
      username: string;
    }
  };

}
