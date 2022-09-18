import React from "react";
import { useSearchParams } from "react-router-dom";
import { ApiError } from "../../casualcms/domain/ports";
import { useConfig } from "../../config";
import { Loader } from "../layout/loader";
import { useAuth } from "../login/hooks";

export const PagePreview: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  const config = useConfig();
  const token = auth.authenticatedUser?.token || "";
  const [previewContent, setPreviewContent] = React.useState<string | null>(
    null
  );
  const [error, setError] = React.useState<ApiError>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [params, setParams] = useSearchParams();
  const pagePath = params.get("page") || "";

  React.useEffect(() => {
    async function loadPage() {
      const page = await config.api.draft.previewDraft(token, pagePath || "");
      console.log(page);
      page
        .map((page: string) => setPreviewContent(page))
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    if (token) {
      loadPage();
    }
    return () => {
      setPreviewContent(null);
      setError(null);
    };
  }, [pagePath, auth]);

  if (isLoading) {
    return <Loader label="loading page..." />;
  }
  if (previewContent) {
    console.log("Replacing content");
    document.body.innerHTML = previewContent;
  }

  return <></>;
};
