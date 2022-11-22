import React from "react";
import { Box, Button, Heading, Icon, Stack } from "@chakra-ui/react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../login/hooks";
import { ApiError } from "../../../casualcms/domain/ports";
import { AppContext } from "../../../config";
import { Snippet, SnippetType } from "../../../casualcms/domain/model";
import { Loader } from "../../components/loader";
import { ApiErrorUI } from "../../components/error_api";
import { SnippetBreadcrumb } from "../../components/breadcrumb";
import { SnippetDeletePopoverForm } from "./snippet_delete";
import { Form } from "../../components/jsonschema_form";
import { DownloadIcon } from "@chakra-ui/icons";

export const SnippetEdit: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  const config = React.useContext(AppContext);
  const token = auth.authenticatedUser?.token || "";
  const [snippet, setSnippet] = React.useState<Snippet | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const params = useParams();
  const snippetKey = params.snippetKey || "";

  const [snippetType, setSnippetType] = React.useState<SnippetType | null>(
    null
  );
  const [error, setError] = React.useState<ApiError>(null);
  let navigate = useNavigate();

  React.useEffect(() => {
    async function loadSnippetType() {
      if (!snippet) {
        return;
      }
      const rtyp = await config.api.snippetType.showSnippetType(
        token,
        snippet.metadata.type
      );
      rtyp
        .map((typ: SnippetType) => setSnippetType(typ))
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    loadSnippetType();
    return () => {
      setIsLoading(true);
      setError(null);
      setSnippetType(null);
    };
  }, [snippet]);

  React.useEffect(() => {
    async function loadSnippet() {
      const rsnippet = await config.api.snippet.showSnippet(token, snippetKey);
      // console.log(rsnippet)
      rsnippet
        .map((snippet: Snippet) => setSnippet(snippet))
        .mapErr((err: ApiError) => setError(err));
    }
    if (token) {
      loadSnippet();
    }
    return () => {
      setSnippet(null);
      setError(null);
    };
  }, [auth, snippetKey]);

  if (isLoading) {
    return <Loader label="Loading form..." />;
  }
  const onsubmit = async (data: any) => {
    const snippet = data.formData;
    await config.api.snippet.updateSnippet(token, snippetKey, snippet);
    navigate(`/admin/snippets`, { replace: true });
  };

  return (
    <Box minW="720px">
      <Heading>Edit Snippet</Heading>
      <SnippetBreadcrumb snippet={snippet} />
      <ApiErrorUI error={error} />
      {snippet && snippetType && (
        <>
          <Form
            id="edit-snippet"
            schema={snippetType.schema}
            uiSchema={snippetType.uiSchema}
            formData={snippet}
            // onChange={() => console.log("changed")}
            onSubmit={onsubmit}
          // onError={() => console.log("errors")}
          />
          <Stack paddingTop={5} direction="row" align="right">
            <Button form="edit-snippet" type="submit" colorScheme="cyan">
              <Icon as={DownloadIcon} marginEnd={2} />
              Save
            </Button>
            <SnippetDeletePopoverForm curSnippet={snippet} />
          </Stack>
        </>
      )}
    </Box>
  );
};
