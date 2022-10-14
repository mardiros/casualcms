import React from "react";
import validator from "@rjsf/validator-ajv6";
import { Box, Heading } from "@chakra-ui/react";
import { withTheme } from "@rjsf/core";
import { Theme as ChakraUITheme } from "@rjsf/chakra-ui";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../login/hooks";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";
import { SnippetType } from "../../casualcms/domain/model";
import { Loader } from "../layout/loader";
import { ApiErrorUI } from "../layout/error_api";
import { SnippetBreadcrumb } from "../layout/breadcrumb";

const Form = withTheme(ChakraUITheme);

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
      <Box maxW="720px">
        {snippetType && (
          <Form
            schema={snippetType.schema}
            uiSchema={snippetType.uiSchema}
            formData={data}
            validator={validator}
            // onChange={() => console.log("changed")}
            onSubmit={onsubmit}
          // onError={() => console.log("errors")}
          />
        )}
      </Box>
    </Box>
  );
};
