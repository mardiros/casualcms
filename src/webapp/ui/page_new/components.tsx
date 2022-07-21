import { v1 as uuidv1 } from "uuid";
import React from "react";
import { Box } from "@chakra-ui/react";
import { withTheme } from "@rjsf/core";
import { Theme as ChakraUITheme } from "@rjsf/chakra-ui";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useAuth } from "../login/hooks";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";
import { PageTemplate } from "../../casualcms/domain/model";
import { Loader } from "../loader/components";
import { ApiErrorUI } from "../errorApi/components";

const Form = withTheme(ChakraUITheme);

export const PageNew: React.FunctionComponent<{}> = () => {
  // console.log("-------------------------------------------")
  // console.log("# Rendering page new")
  let { tpltype } = useParams<string>();
  let auth = useAuth();
  const config = React.useContext(AppContext);
  const token = auth.authenticatedUser?.token || "";
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [template, setTemplate] = React.useState<PageTemplate | null>(null);
  const [error, setError] = React.useState<ApiError>(null);
  let navigate = useNavigate();
  const [params, setParams] = useSearchParams();
  const parent = params.get("parent");
  React.useEffect(() => {
    async function loadTemplate() {
      const template = await config.api.template.showTemplate(
        token,
        tpltype || ""
      );
      template
        .map((tpl: PageTemplate) => setTemplate(tpl))
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    loadTemplate();
    return () => {
      setIsLoading(true);
      setError(null);
      setTemplate(null);
    };
  }, [tpltype]);

  if (isLoading) {
    return <Loader label="Loading form..." />;
  }
  const onsubmit = async (data: any) => {
    const page = data.formData;
    await config.api.page.createPage(token, tpltype || "", page, parent);
    navigate(`/admin/pages?${params}`, { replace: true });
  };

  const data = { id: uuidv1() };
  return (
    <Box maxW="720px">
      <ApiErrorUI error={error} />
      {template && (
        <Form
          schema={template.schema}
          uiSchema={template.uiSchema}
          formData={data}
          // onChange={() => console.log("changed")}
          onSubmit={onsubmit}
          // onError={() => console.log("errors")}
        />
      )}
    </Box>
  );
};
