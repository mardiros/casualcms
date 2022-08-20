import React from "react";
import { Box, Heading } from "@chakra-ui/react";
import { withTheme } from "@rjsf/core";
import { Theme as ChakraUITheme } from "@rjsf/chakra-ui";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useAuth } from "../login/hooks";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";
import { Snippet, SnippetType } from "../../casualcms/domain/model";
import { Loader } from "../layout/loader";
import { ApiErrorUI } from "../layout/error_api";
import { SnippetBreadcrumb } from "../layout/breadcrumb";
import { SnippetDeletePopoverForm } from "./snippet_delete";

const Form = withTheme(ChakraUITheme);

export const SnippetEdit: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  const config = React.useContext(AppContext);
  const token = auth.authenticatedUser?.token || "";
  const [snippet, setSnippet] = React.useState<Snippet | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const params = useParams();
  const snippetSlug = params.snippetSlug || "";

  const [template, setTemplate] = React.useState<SnippetType | null>(null);
  const [error, setError] = React.useState<ApiError>(null);
  let navigate = useNavigate();

  React.useEffect(() => {
    async function loadTemplate() {
      if (!snippet) {
        return;
      }
      const template = await config.api.snippetType.showSnippetType(
        token,
        snippet.meta.type
      );
      template
        .map((tpl: SnippetType) => setTemplate(tpl))
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    loadTemplate();
    return () => {
      setIsLoading(true);
      setError(null);
      setTemplate(null);
    };
  }, [snippet]);

  React.useEffect(() => {
    async function loadSnippet() {
      const page = await config.api.snippet.showSnippet(token, snippetSlug);
      // console.log(page)
      page
        .map((page: Snippet) => setSnippet(page))
        .mapErr((err: ApiError) => setError(err));
    }
    loadSnippet();
    return () => {
      setSnippet(null);
      setError(null);
    };
  }, [snippetSlug]);

  if (isLoading) {
    return <Loader label="Loading form..." />;
  }
  const onsubmit = async (data: any) => {
    const snippet = data.formData;
    await config.api.snippet.updateSnippet(token, snippetSlug, snippet);
    navigate(`/admin/snippets`, { replace: true });
  };

  return (
    <Box maxW="720px">
      <Heading>Edit Snippet</Heading>
      <SnippetBreadcrumb snippet={snippet} />
      <ApiErrorUI error={error} />
      {snippet && template && (
        <>
          <Form
            schema={template.schema}
            uiSchema={template.uiSchema}
            formData={snippet}
            // onChange={() => console.log("changed")}
            onSubmit={onsubmit}
            // onError={() => console.log("errors")}
          />
          <SnippetDeletePopoverForm curSnippet={snippet} />
        </>
      )}
    </Box>
  );
};
