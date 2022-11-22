import React from "react";
import { Box, Button, Heading, Icon, Stack } from "@chakra-ui/react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../login/hooks";
import { ApiError } from "../../../casualcms/domain/ports";
import { AppContext } from "../../../config";
import { SnippetType } from "../../../casualcms/domain/model";
import { Loader } from "../../components/loader";
import { ApiErrorUI } from "../../components/error_api";
import { SnippetBreadcrumb } from "../../components/breadcrumb";
import { Form } from "../../components/jsonschema_form";
import { DownloadIcon } from "@chakra-ui/icons";

export const SnippetNew: React.FunctionComponent<{}> = () => {
  let { snippetTypeName } = useParams<string>();
  let auth = useAuth();
  const config = React.useContext(AppContext);
  const token = auth.authenticatedUser?.token || "";
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [snippetType, setSnippetType] = React.useState<SnippetType | null>(
    null
  );
  const [error, setError] = React.useState<ApiError>(null);
  let navigate = useNavigate();

  React.useEffect(() => {
    async function loadType() {
      const rtyp = await config.api.snippetType.showSnippetType(
        token,
        snippetTypeName || ""
      );
      rtyp
        .map((typ: SnippetType) => setSnippetType(typ))
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    if (token) {
      loadType();
    }
    return () => {
      setIsLoading(true);
      setError(null);
      setSnippetType(null);
    };
  }, [auth, snippetTypeName]);

  if (isLoading) {
    return <Loader label="Loading form..." />;
  }
  const onsubmit = async (data: any) => {
    const snippet = data.formData;
    await config.api.snippet.createSnippet(
      token,
      snippetTypeName || "",
      snippet
    );
    navigate(`/admin/snippets`, { replace: true });
  };

  const data = {};
  return (
    <Box minW="720px">
      <Heading>New Snippet</Heading>
      <SnippetBreadcrumb title="new snippet" />
      <ApiErrorUI error={error} />
      {snippetType && (
        <>
          <Box maxW="720px">
            <Form
              id="new-snippet"
              schema={snippetType.schema}
              uiSchema={snippetType.uiSchema}
              formData={data}
              // onChange={() => console.log("changed")}
              onSubmit={onsubmit}
            // onError={() => console.log("errors")}
            />
          </Box>
          <Stack paddingTop={5} direction="row" align="right">
            <Button form="new-snippet" type="submit" colorScheme="cyan">
              <Icon as={DownloadIcon} marginEnd={2} />
              Create Snippet
            </Button>
          </Stack>
        </>
      )}
    </Box>
  );
};
